int adder(int a, int b){
    int c = a + b;
    return c;
}

int top(int d, int e, int g, int h, int k, int l){
    int c = adder(d, e);
    int f = adder(g, h);
    int j = adder(k, l);

    int result = 0;
    if (c < f){
        result = f + j;
    }else{
        result = c + j;
    }
    return result;
}
