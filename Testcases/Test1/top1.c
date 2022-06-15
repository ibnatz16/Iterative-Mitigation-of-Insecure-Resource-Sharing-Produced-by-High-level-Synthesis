int top(int a, int b, int d, int m, int n, int p, int y) {
    int c = a + b;
    int e = d * c;    
    int f = m * n;    
    int g = f * p;
    int h = g + c;
    int x = 0;
    if (a > 10)
       x = e + g + y;
    else
       x = h + d;
    return x;
}
