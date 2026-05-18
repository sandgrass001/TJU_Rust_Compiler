fn main() -> i32 {
    let mut a:i32 = 10;
    let mut b = 20;
    while a > 0 {
        a = a - 1;
        if a == 5 {
            b = b + 1;
        }
    }
    return b;
}