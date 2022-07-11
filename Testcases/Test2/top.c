int top (int a, int b, int c, int d, int e){
    int f, g, h;
    for (int i = 0; i < 10; i++){
        if (a > 10 && (a % b ==0)){
            f = a/b;
        }else{
            f = a * b;
            g = c + d + e;
            if (g % e == 0)
                h = g/e;
        }
    }
    int result = f + h;
    return result;
}
