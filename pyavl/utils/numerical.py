'''
Created on Jul 16, 2009

@author: pankaj
'''

def false_position_method(func, x0, x1, epsilon, max_iter=100):
    '''the false position (secant) method to solve a non-linear equation
    returns x,y of the solution'''
    y0 = func(x0)
    y1 = func(x1)
    for i in xrange(max_iter):
        if y1 == y0 or -epsilon < y1 < epsilon:
            break
        x2 = x1 - y1 * (x1 - x0) / (y1 - y0)
        x0, x1 = x1, x2
        y0, y1 = y1, func(x1)
    print 'iterations =', i
    return x1, y1
    
if __name__ == '__main__':
    import math
    func = math.cos
    print false_position_method(func, 0.0, 1.0, 1e-6)
    