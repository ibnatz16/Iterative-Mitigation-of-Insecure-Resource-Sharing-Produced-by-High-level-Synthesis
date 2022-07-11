int top (int a, int b, int c, int d, int e){
    int f, g, h, i, j;
    while(f < 10){
        if ((a % b) == 0){
            g = a / b;
        }else{
            g = a * b;
        }

        h = c * d;

        if ((h % 2) == 0){
            f = g + h;
        }else{
            f = g * h;
        }

        i = d * e;
        j = f * i;
    }
    return j;
}
