def cherry(x : float) -> float:
    return 0.0022222953007 * x*x -2.6841711030313 *x + 2041.3006018947

def start( x : float ) -> float:
    return 0.2 * ( cherry( x ) - 1500 )
