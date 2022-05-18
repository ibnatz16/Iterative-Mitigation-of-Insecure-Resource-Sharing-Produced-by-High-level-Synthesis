from __future__ import print_function
import argparse
from ast import arg

from pycparser import parse_file, c_generator

operations = {"plus": "+", "mult": "*"}
secure_ops = []

def res_share():
    f = open("resource_sharing.txt")
    lines = f.readlines()
    for line in lines:
        if len(lines) == 2:
            if line.find("Resources") != -1:
                res = [op for op in operations if op in line]
                resource = res[0]
                return resource
    return 0

def insecure_op(resource):
    operator = ""
    for op in operations:
        if op == resource:
            operator = operations[op]
    return operator

def get_secure(ast, asset, assets):
    
    assets.append(asset)
    children = ast.children()

    for child in children:
        for block in child[1].body.block_items:
            if block.__class__.__name__ == "Decl":
                var = block.name
                init = block.init
                if init.__class__.__name__ == "BinaryOp":
                    if init.left.__class__.__name__ == "ID" or init.right.__class__.__name__ == "ID":
                        if init.left.__class__.__name__ == "ID":
                            if init.left.name in assets:
                                assets.append(var)
                            else:
                                if init.right.__class__.__name__ == "ID":
                                    if init.right.name in assets:
                                        assets.append(var)
                elif init.__class__.__name__ == "Constant":
                    pass

def ast_traversal(ast, check_resource, assets):
    children = ast.children()
    for child in children:
        for block in child[1].body.block_items:
            if block.__class__.__name__ == "Decl":
                var = block.name
                init = block.init
                if init.__class__.__name__ == "BinaryOp":
                    if check_resource == 1:
                        resource = res_share()
                        operator = insecure_op(resource)
                        if init.op == operator:
                            if var in assets:
                                secure_ops.append(var)

def fix_params(child, old_params):
    new_params = []
    decl_vars = []
    for block in child.body.block_items:
        if block.__class__.__name__ == "Decl":
            init = block.init
            decl_vars.append(block.name)
            if init.__class__.__name__ == "BinaryOp":
                if init.left.name not in new_params and init.left.name not in decl_vars:
                    new_params.append(init.left.name)
                if init.right.name not in new_params and init.right.name not in decl_vars:
                    new_params.append(init.right.name)
    return new_params

def make_ast(ast):
    children = ast.children()
    for child in children:
        c = 0
        block_remove = []
        index = -1
        name = ""
        var_type = ""
        for block in child[1].body.block_items:
            index+=1
            if block.__class__.__name__ == "Decl":
                if block.name not in secure_ops:
                    block_remove.append(block)
                else:
                    name = block.name
                    var_type = block.type.type
            elif block.__class__.__name__ == "If":
                left_var = ""
                right_var = ""
                if block.cond.left.__class__.__name__ == "ID":
                    left_var = block.cond.left.name
                if block.cond.right.__class__.__name__ == "ID":
                    right_var = block.cond.right.name
                if (left_var not in secure_ops) or (right_var not in secure_ops):
                    if block.iftrue.lvalue.__class__.__name__ == "ID":
                        if block.iftrue.lvalue.name not in secure_ops:
                            if block.iffalse.lvalue.__class__.__name__ == "ID":
                                if block.iftrue.lvalue.name not in secure_ops:
                                    block_remove.append(block)
                                else:
                                    name = block.iftrue.lvalue.name
                                    var_type = block.type.type
            elif block.__class__.__name__ == "Return":
                block.expr.name = name

        if block_remove:
            for rm in block_remove:
                child[1].body.block_items.remove(rm)

        old_params = []
        for decl in child[1].decl:
            c += 1
            decl.type.type = var_type
            ft_name = decl.type.declname
            decl.type.declname = "%s%s" % (ft_name, c)
            filename = "%s.c" % decl.type.declname
            param_list = decl.args.params
            for param in param_list:
                old_params.append(param.name)
            new_params = fix_params(child[1], old_params)
            i = 0
            j = 0
            while i != len(new_params):
                if new_params[i] not in old_params:
                    if param_list[j].name not in new_params:
                        param_list[j].name = new_params[i]
                        param_list[j].type.declname = new_params[i]
                        j+=1
                        i+=1
                    else:
                        j+=1
                else:
                    i+=1
                
            decl.args.params = param_list
            param_rm = []
            if i == len(new_params):
                for param in param_list:
                    if param.name not in new_params:
                        # decl.args.params.remove(param)
                        param_rm.append(param)
            
            for rem in param_rm:
                decl.args.params.remove(rem)
                    
    return ast, filename

def change_top (ast, top, new):
    var_list = []
    top_module = ""
    params = []
    if new.find("."):
        top_module = new[0:new.find(".")]
    for child in ast.children():
        body = child[1].body
        decl = child[1].decl
        for param in decl.type.args.params:
            params.append(param.name)
        for block in body.block_items:
            if block.__class__.__name__ == "Decl":
                var_type = block.type.type.names[0]
                var_name = block.name
                var = "%s %s" % (var_type, var_name)
    param_str = ", ".join(map(str,params))
    file = open(top, "r")
    list_of_lines = file.readlines()
    index = 0
    change_index = 0
    new_line = ""
    for line in list_of_lines:
        # line = line.strip()
        if line.find(var) != -1:
            indent = line[0:line.find(var)]
            new_line = "%s%s = %s(%s);\n" % (indent, var, top_module, param_str)
            change_index = index
        index += 1
    list_of_lines[change_index] = new_line
    res = open("../Result/%s"%top, "w")
    res.writelines(list_of_lines)
    res.close()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser('Dump AST')
    argparser.add_argument('filename',
                           default='top.c',
                           nargs='?',
                           help='name of file to parse')
    argparser.add_argument('secure_asset', default='b',
                            help="asset to separate")
    argparser.add_argument('--coord', help='show coordinates in the dump',
                           action='store_true')
    args = argparser.parse_args()

    ast = parse_file(args.filename, use_cpp=False)

    asset = "b"
    assets = []
    check_resource = 1
    get_secure(ast, asset, assets)
    ast_traversal(ast, check_resource, assets)
    new_ast, filename = make_ast(ast)
    generator = c_generator.CGenerator()
    #generator.visit(new_ast)
    #filename = "top1.c"
    f = open("../Result/%s" % filename, "w")
    f.write(generator.visit(new_ast))
    change_top(new_ast, args.filename, filename)
    #file_no+=1
