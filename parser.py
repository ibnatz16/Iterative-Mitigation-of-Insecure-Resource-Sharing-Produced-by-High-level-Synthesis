from __future__ import print_function
import argparse
from ast import AsyncFunctionDef, arg
from pycparser import parse_file, c_generator, c_parser, c_ast

operations = {"plus": "+", "mult": "*", "rshift": "/"}
secure_ops = []

def res_share():
    f = open("resource_sharing.txt")
    lines = f.readlines()
    resource = ""
    for line in lines:
        #if len(lines) == 2:
        if line.find("Resources") != -1:
            res = [op for op in operations if op in line]
            resource = res[0]
        elif line.find("Secure Asset") !=-1:
            op_index = line.find("[['")
            end_index = line.find("']]")
            substr = line[op_index+3:end_index]
            ls = substr.split("', '")
    return resource, ls

def insecure_op(resource):
    operator = ""
    for op in operations:
        if op == resource:
            operator = operations[op]
    return operator

def binary_op(init, assets, var, unit):
    if init.left.__class__.__name__ == "ID" or init.right.__class__.__name__ == "ID":
        if init.left.__class__.__name__ == "ID":
            if init.left.name == unit:
                assets.append(var)
            else:
                if init.right.__class__.__name__ == "ID":
                    if init.right.name == unit:
                        assets.append(var)
        elif init.left.__class__.__name__ == "BinaryOp":
            binary_op(init.left, assets, var, unit)

def get_secure(block, assets, check_resource, path):

    for child in children:
        for block in child[1].body.block_items:
            if block.__class__.__name__ == "Decl":
                var = block.name
                init = block.init
                if init.__class__.__name__ == "BinaryOp":
                    if check_resource == 1:
                        
                        if init.op == operator:
                            if var in assets:
                                secure_ops.append(var)
                    else:
                        if init.left.__class__.__name__ == "ID" and init.right.__class__.__name__ == "ID":
                                lname = init.left.name
                                rname = init.right.name
                                binaryop = init.op
                                for p in path:
                                    if lname in p and rname in p and binaryop in p:
                                        unit = var
                        binary_op(init, assets, var, unit)
                elif init.__class__.__name__ == "Constant":
                    pass
            elif block.__class__.__name__ == "If":
                # Check true and false blocks
                cond = block.cond
                true = block.iftrue
                false = block.iffalse
                if cond.right.__class__.__name__ == "Constant":
                    pass

                if true.__class__.__name__ == "Compound":
                    #Loop through each item
                    for item in true.block_items:
                        if item.__class__.__name__ == "Assignment":
                            # Check the right hand side
                            if item.rvalue.__class__.__name__ == "BinaryOp":
                                op = item.rvalue
                                var = item.lvalue.name
                                # unit = ""
                                if check_resource == 1:

                                    if op.op == operator:
                                        if var in assets:
                                            secure_ops.append(var)
                                else:
                                    if op.left.__class__.__name__ == "ID" and op.right.__class__.__name__ == "ID":
                                        lname = op.left.name
                                        rname = op.right.name
                                        binaryop = op.op
                                        for p in path:
                                            if lname in p and rname in p and binaryop in p:
                                                unit = var
                                    
                                    if op.left.__class__.__name__ == "ID":
                                        if op.left.name == unit:
                                            assets.append(var)
                                        else:
                                            if op.right.__class__.__name__ == "ID":
                                                if op.right.name == unit:
                                                    assets.append(var)
                elif true.__class__.__name__ == "Assignment":
                    var = true.lvalue.name
                    if true.rvalue.__class__.__name__ == "BinaryOp":
                        if check_resource == 1:
                           
                            if true.rvalue.op == operator:
                                if var in assets:
                                    secure_ops.append(var)
                        else:
                            if true.rvalue.left.__class__.__name__ == "ID" and true.rvalue.right.__class__.__name__ == "ID":
                                lname = true.rvalue.left.name
                                rname = true.rvalue.right.name
                                binaryop = true.rvalue.op
                                for p in path:
                                    if lname in p and rname in p and binaryop in p:
                                        unit = var
                            binary_op(true.rvalue, assets, var, unit)

                if false.__class__.__name__ == "Compound":
                    for item in false.block_items:
                        if item.__class__.__name__ == "Assignment":
                            # Check the right hand side
                            if item.rvalue.__class__.__name__ == "BinaryOp":
                                op = item.rvalue
                                var = item.lvalue.name
                                if check_resource == 1:
                                    
                                    if op.op == operator:
                                        if var in assets:
                                            secure_ops.append(var)
                                else:
                                    if op.left.__class__.__name__ == "ID" and op.right.__class__.__name__ == "ID":
                                        lname = op.left.name
                                        rname = op.right.name
                                        binaryop = op.op
                                        for p in path:
                                            if lname in p and rname in p and binaryop in p:
                                                unit = var
                                    
                                    if op.left.__class__.__name__ == "ID":
                                        if op.left.name == unit:
                                            assets.append(var)
                                        else:
                                            if op.right.__class__.__name__ == "ID":
                                                if op.right.name == unit:
                                                    assets.append(var)
                elif false.__class__.__name__ == "Assignment":
                    var = false.lvalue.name
                    if false.rvalue.__class__.__name__ == "BinaryOp":
                        if check_resource == 1:
                            
                            if false.rvalue.op == operator:
                                if var in assets:
                                    secure_ops.append(var)
                        else:
                            if false.rvalue.left.__class__.__name__ == "ID" and false.rvalue.right.__class__.__name__ == "ID":
                                lname = false.rvalue.left.name
                                rname = false.rvalue.right.name
                                binaryop = false.rvalue.op
                                for p in path:
                                    if lname in p and rname in p and binaryop in p:
                                        unit = var
                            binary_op(false.rvalue, assets, var, unit)

def make_ast(ast):
    new_children = ast.children()
    for child in new_children:
        decl = child[1].decl
        body = child[1].body
        c = 0 # count for params
        new_params = []
        variables = []
        first = 0
        block_remove = []
        block_name = ""
        # Check if the return type is int
        if decl.type.type.type.names[0] == 'int':
            ft_name = decl.type.type.declname
            decl.type.type.declname = "%s%s" % (ft_name, '1')
            filename = "%s.c" % decl.type.type.declname
            params = decl.type.args.params
            
            # We only need two parameters for a binary operation
            for param in params:
                if c != 2:
                    new_params.append(param)
                    variables.append(param.name)
                    c+=1
                else:
                    break
            decl.type.args.params = new_params
        
        # Make the body only the binary operation needed and the return
        for block in body.block_items:
            if block.__class__.__name__ == "Decl" and first == 0:
                left_id = c_ast.ID(variables[0])
                right_id = c_ast.ID(variables[1])
                new_init = c_ast.BinaryOp(operator,left_id,right_id)
                block.init = new_init
                first+=1
                block_name = block.name
            elif block.__class__.__name__ == "Return":
                block.expr = c_ast.ID(block_name)
            else:
                block_remove.append(block)

        # Remove the unneeded blocks
        if block_remove:
            for rm in block_remove:
                child[1].body.block_items.remove(rm)

    return ast, filename

def assignment (a_block, operator, assets, params, var_list):
    if a_block.__class__.__name__ == "Assignment":
        if a_block.lvalue.name in assets and a_block.rvalue.__class__.__name__ == "BinaryOp":
            if a_block.rvalue.op == operator:
                # var_type = a_block.lvalue.type.type.names[0]
                # var_name = a_block.lvalue.name
                # var = "%s %s" % (var_type, var_name)
                temp_var = [v for v in var_list if a_block.lvalue.name in v]
                if temp_var[0] != "":
                    params.append(a_block.rvalue.left.name)
                    params.append(a_block.rvalue.right.name)
                    return temp_var[0]
    return ""

def change_top (ast, assets, operator, top, new):
    var_list = []
    top_module = ""
    params = []
    var = []
    if new.find("."):
        top_module = new[0:new.find(".")]
    for child in ast.children():
        body = child[1].body
        # decl = child[1].decl
        var_list = []
        # for param in decl.type.args.params:
        #     params.append(param.name)
        for block in body.block_items:
            if block.__class__.__name__ == "Decl": 
                if block.init.__class__.__name__ == "BinaryOp":
                    if block.name in assets and block.init.op == operator:
                        var_type = block.type.type.names[0]
                        var_name = block.name
                        var.append("%s %s" % (var_type, var_name))
                        params.append(block.init.left.name)
                        params.append(block.init.right.name)
                        break
                elif block.init.__class__.__name__ == "Constant" and block.name in assets:
                    var_list.append(block.name)
            elif block.__class__.__name__ == "If":
                false_block = block.iffalse
                true_block = block.iftrue
                if true_block.__class__.__name__ == "Compound":
                    for a_block in true_block.block_items:
                        if a_block.rvalue.__class__.__name__ == "BinaryOp":
                            if a_block.rvalue.op == operator:
                                result = assignment(a_block, operator, assets, params, var_list)
                                if result != "":
                                    var.append(result)
                elif true_block.__class__.__name__ == "Assignment":
                    result = assignment(true_block, operator, assets, params, var_list)
                    if result != "":
                        var.append(result)
                if false_block.__class__.__name__ == "Compound":
                    for a_block in false_block.block_items:
                        if a_block.rvalue.__class__.__name__ == "BinaryOp":
                            if a_block.rvalue.op == operator:
                                result = assignment(a_block, operator, assets, params, var_list)
                                if result != "":
                                    var.append(result)
                elif false_block.__class__.__name__ == "Assignment":
                    result = assignment(false_block, operator, assets, params, var_list, var)
                    if result != "":
                        var.append(result)
    param_str = ", ".join(map(str,params))
    file = open(top, "r")
    list_of_lines = file.readlines()
    index = 0
    change_index = 0
    new_line = ""
    for line in list_of_lines:
        # line = line.strip()
        if line.find(var[0]) != -1 and line.find(operator) !=-1:
            indent = line[0:line.find(var[0])]
            new_line = "%s%s = %s(%s);\n" % (indent, var[0], top_module, param_str)
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
    #ast.show()
    asset = args.secure_asset
    assets = []
    children = ast.children()
    check_resource = 0

    assets.append(asset)
    resource, ls = res_share()
    count = 0
    for p in ls:
        if p.find("int")!=-1:
            start = p.find("int")
            p = p[start+5:]
            end = p.find(")")
            p = p[0:end]
            ls[count] = p
        count +=1
    operator = insecure_op(resource)

    get_secure(children, assets, check_resource, ls) # works well

    assets = list(set(assets))
    print(assets)

    #print(operator)
    check_resource = 1
    get_secure(children, assets, check_resource, ls)
    print(secure_ops)
    new_ast, filename = make_ast(ast)
    # new_ast.show()
    ast = parse_file(args.filename, use_cpp=False)
    generator = c_generator.CGenerator()
    #generator.visit(new_ast)
    #filename = "top1.c"
    f = open("../Result/%s" % filename, "w")
    f.write(generator.visit(new_ast))
    change_top(ast, assets, operator, args.filename, filename)
    #file_no+=1
