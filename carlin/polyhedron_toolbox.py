r"""
Numerical computations with polytopes, with a focus on computational geometry.

Features:

- an "abstract" Polyhedron class 
- computations with support functions
- Hausdorff distance computation, exact and approximate algorithms
- polytope projections via Lotov's algorithm
- a bunch of commonly used functions

AUTHOR:

- Marcelo Forets  (first draft: 20 Oct 2016)
                  (last modified: 10 Feb 2017)
"""

#************************************************************************
#       Copyright (C) 2016 Marcelo Forets <mforets@nonlinearnotes.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#                  http://www.gnu.org/licenses/
#************************************************************************

# Sage objects
from sage.rings.rational_field import QQ

def polyhedron_to_Hrep(P, separate_equality_constraints = False):
    r"""Extract half-space representation of an input polytope P. 
    
    By default, returns matrices [A, b] representing P as Ax <= b. 
    If separate_equality_constraints = True, returns matrices [A, b, Aeq, beq], 
    with separated inequality and equality constraints.

    INPUT:

    * "P" - object of class polyhedron

    * "separate_equality_constraints" - (default = False) If True, returns Aeq, beq containing the equality constraints, 
    removing the corresponding lines from A and b.

    OUTPUT:

    * "[A, b]" - dense matrix and vector respectively (dense, RDF).

    * "[A, b, Aeq, beq]" - (if the flag separate_equality_constraints is True), matrices and vectors (dense, RDF). 
    
    NOTES::
    
    - Equality constraints are removed from A and put into Aeq.

    EXAMPLES::

    sage: A = matrix(RDF, [[-1.0, 0.0,  0.0,  0.0,  0.0,  0.0],
    ....: [ 1.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    ....: [ 0.0,  1.0,  0.0,  0.0,  0.0,  0.0],
    ....: [ 0.0, -1.0,  0.0,  0.0,  0.0,  0.0],
    ....: [0.0,  0.0, -1.0,  0.0,  0.0,  0.0],
    ....: [0.0,  0.0,  1.0,  0.0,  0.0,  0.0],
    ....: [0.0,  0.0,  0.0, -1.0,  0.0,  0.0],
    ....: [0.0,  0.0,  0.0,  1.0,  0.0,  0.0],
    ....: [0.0,  0.0,  0.0,  0.0,  1.0,  0.0],
    ....: [0.0,  0.0,  0.0,  0.0, -1.0,  0.0],
    ....: [0.0,  0.0,  0.0,  0.0,  0.0,  1.0],
    ....: [0.0,  0.0,  0.0,  0.0,  0.0, -1.0]])
    sage: b = vector(RDF, [0.0, 10.0, 0.0, 0.0, 0.2, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0])
    sage: P = polyhedron_from_Hrep(A, b, base_ring = RDF); P
    A 3-dimensional polyhedron in RDF^6 defined as the convex hull of 8 vertices

    sage: [A, b] = polyhedron_to_Hrep(P)
    sage: A
    [-0.0  1.0 -0.0 -0.0 -0.0 -0.0]
    [ 0.0 -1.0  0.0  0.0  0.0  0.0]
    [-0.0 -0.0 -0.0 -0.0  1.0 -0.0]
    [ 0.0  0.0  0.0  0.0 -1.0  0.0]
    [-0.0 -0.0 -0.0 -0.0 -0.0  1.0]
    [ 0.0  0.0  0.0  0.0  0.0 -1.0]
    [-1.0 -0.0 -0.0 -0.0 -0.0 -0.0]
    [ 1.0 -0.0 -0.0 -0.0 -0.0 -0.0]
    [-0.0 -0.0 -1.0 -0.0 -0.0 -0.0]
    [-0.0 -0.0  1.0 -0.0 -0.0 -0.0]
    [-0.0 -0.0 -0.0 -1.0 -0.0 -0.0]
    [-0.0 -0.0 -0.0  1.0 -0.0 -0.0]
    sage: b
    (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 0.2, 0.2, 0.1, 0.1)

    NOTES::

    - This function is used to revert the job of polytopeFromHalfSpaceRep(A, b, base_ring = RDF). 
    - However, it is not the inverse generally, because of: 
        - automatic reordering of rows (this is uncontrolled, internal to Polyhedron), and 
        - scaling. In the example of above, with a polyhedron in RDF we see reordering of rows. 
        
    TESTS:: 
    
    If we choose QQ, then we have both reordering and rescaling::

    sage: P = polyhedron_from_Hrep(A, b, base_ring = QQ); P
    A 3-dimensional polyhedron in QQ^6 defined as the convex hull of 8 vertices

    sage: [A, b] = polyhedron_to_Hrep(P)
    sage: A
    [  0.0   0.0   0.0   0.0   0.0  -1.0]
    [  0.0   0.0   0.0   0.0   0.0   1.0]
    [  0.0   0.0   0.0   0.0  -1.0   0.0]
    [  0.0   0.0   0.0   0.0   1.0   0.0]
    [  0.0  -1.0   0.0   0.0   0.0   0.0]
    [  0.0   1.0   0.0   0.0   0.0   0.0]
    [ -1.0   0.0   0.0   0.0   0.0   0.0]
    [  0.0   0.0   5.0   0.0   0.0   0.0]
    [  0.0   0.0  -5.0   0.0   0.0   0.0]
    [  0.0   0.0   0.0 -10.0   0.0   0.0]
    [  0.0   0.0   0.0  10.0   0.0   0.0]
    [  1.0   0.0   0.0   0.0   0.0   0.0]
    sage: b
    (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 10.0)

    The polytope P is not full-dimensional. To extract the equality constraints we use the flag separate_equality_constraints::

    sage: [A, b, Aeq, beq] = polyhedron_to_Hrep(P, separate_equality_constraints = True)
    sage: A
    [ -1.0   0.0   0.0   0.0   0.0   0.0]
    [  0.0   0.0   5.0   0.0   0.0   0.0]
    [  0.0   0.0  -5.0   0.0   0.0   0.0]
    [  0.0   0.0   0.0 -10.0   0.0   0.0]
    [  0.0   0.0   0.0  10.0   0.0   0.0]
    [  1.0   0.0   0.0   0.0   0.0   0.0]
    sage: b
    (0.0, 1.0, 1.0, 1.0, 1.0, 10.0)
    sage: Aeq
    [ 0.0  0.0  0.0  0.0  0.0 -1.0]
    [ 0.0  0.0  0.0  0.0 -1.0  0.0]
    [ 0.0 -1.0  0.0  0.0  0.0  0.0]
    sage: beq
    (0.0, 0.0, 0.0)
"""
    if not separate_equality_constraints:
        # a priori I don't know number of equalities; actually m may be bigger than len(P.Hrepresentation()) !
        # for this, we should transform equalities into inequalities, so that Ax <= b is correct.
        b = list(); A = list()

        P_gen = P.Hrep_generator();

        for pigen in P_gen:
            if (pigen.is_equation()):
                pi_vec = pigen.vector()
                A.append(-pi_vec[1:len(pi_vec)])
                b.append(pi_vec[0])

                A.append(pi_vec[1:len(pi_vec)])
                b.append(pi_vec[0])

            else:
                pi_vec = pigen.vector()
                A.append(-pi_vec[1:len(pi_vec)])
                b.append(pi_vec[0])

        return [matrix(RDF, A), vector(RDF, b)]

    else:
        b = list(); A = list(); beq = list(); Aeq = list()

        P_gen = P.Hrep_generator();

        for pigen in P_gen:
            if (pigen.is_equation()):
                pi_vec = pigen.vector()
                Aeq.append(-pi_vec[1:len(pi_vec)])
                beq.append(pi_vec[0])

            else:
                pi_vec = pigen.vector()
                A.append(-pi_vec[1:len(pi_vec)])
                b.append(pi_vec[0])

    return [matrix(RDF, A), vector(RDF, b), matrix(RDF, Aeq), vector(RDF, beq)]
        
def polyhedron_from_Hrep(A, b, base_ring=QQ):
    r"""Builds a polytope given the H-representation, in the form Ax <= b

    INPUT:

    * "A" - matrix of size m x n, in RDF or QQ ring. Accepts generic Sage matrix, and also a Numpy arrays with a matrix shape.

    * "b" - vector of size m, in RDF or QQ ring. Accepts generic Sage matrix, and also a Numpy array.

    * "base_ring" - (default: QQ). Specifies the ring (base_ring) for the Polyhedron constructor. Valid choices are:

        * QQ - rational. Uses 'ppl' (Parma Polyhedra Library) backend

        * RDF - Real double field. Uses 'cdd' backend.

    OUTPUT:

    * "P" - a Polyhedron object

    TO-DO:

    * accept numpy arrays. notice that we often handle numpy arrays (for instance if we load some data from matlab using the function
    scipy.io.loadmat(...), then the data will be loaded as a dictionary of numpy arrays)

    EXAMPLES:

    sage: A = matrix(RDF, [[-1.0, 0.0,  0.0,  0.0,  0.0,  0.0],
    ....: [ 1.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    ....: [ 0.0,  1.0,  0.0,  0.0,  0.0,  0.0],
    ....: [ 0.0, -1.0,  0.0,  0.0,  0.0,  0.0],
    ....: [ 0.0,  0.0, -1.0,  0.0,  0.0,  0.0],
    ....: [ 0.0,  0.0,  1.0,  0.0,  0.0,  0.0],
    ....: [ 0.0,  0.0,  0.0, -1.0,  0.0,  0.0],
    ....: [ 0.0,  0.0,  0.0,  1.0,  0.0,  0.0],
    ....: [ 0.0,  0.0,  0.0,  0.0,  1.0,  0.0],
    ....: [ 0.0,  0.0,  0.0,  0.0, -1.0,  0.0],
    ....: [ 0.0,  0.0,  0.0,  0.0,  0.0,  1.0],
    ....: [ 0.0,  0.0,  0.0,  0.0,  0.0, -1.0]])

    sage: b = vector(RDF, [0.0, 10.0, 0.0, 0.0, 0.2, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0])
    sage: P = polyhedron_from_Hrep(A, b, base_ring=QQ); P
    A 3-dimensional polyhedron in QQ^6 defined as the convex hull of 8 vertices

    NOTE:

    This function is useful especially when the input matrices A, b are ill-defined 
    (constraints that differ by tiny amounts making the input data to be degenerate or almost degenerate), 
    causing problems to Polyhedron(...). 
    In this case it is recommended to use base_ring = QQ. Each element of A and b will be converted to rational, and this will be sent to Polyhedron.
     Note that Polyhedron automatically removes redundant constraints.

    """

    if (base_ring == RDF):

        if 'numpy.ndarray' in str(type(A)):
            # assuming that b is also a numpy array
            m = A.shape[0]; n = A.shape[1];

            b_RDF = vector(RDF, m, [RDF(bi) for bi in b])

            A_RDF = matrix(RDF, m, n)
            for i in range(m):
                A_RDF.set_row(i, [RDF(A[i][j]) for j in range(n)])

            A = copy(A_RDF);
            b = copy(b_RDF);

        ambient_dim = A.ncols()

        # transform to real, if needed
        if A.base_ring() != RDF:
            A.change_ring(RDF)

        if b.base_ring() != RDF:
            b.change_ring(RDF)

        ieqs_list = []
        for i in range(A.nrows()):
            ieqs_list.append(list(-A.row(i)))  #change in sign, necessary since Polyhedron receives Ax+b>=0
            ieqs_list[i].insert(0,b[i])

        P = Polyhedron(ieqs = ieqs_list, base_ring=RDF, ambient_dim=A.ncols(), backend='cdd')

    elif (base_ring == QQ):

        if 'numpy.ndarray' in str(type(A)):
            # assuming that b is also a numpy array
            m = A.shape[0]; n = A.shape[1];

            b_QQ = vector(QQ, m, [QQ(b[i]) for i in range(m)])
            A_QQ = matrix(QQ, m, n)

            for i in range(m):
                A_QQ.set_row(i, [QQ(A[i][j]) for j in range(n)])

            A = copy(A_QQ);
            b = copy(b_QQ);

        ambient_dim = A.ncols()

        # transform to rational, if needed
        if A.base_ring() != QQ:
            #for i in range(A.nrows()):
            #    A.set_row(i,[QQ(A.row(i)[j]) for j in range(ambient_dim)]);
            A.change_ring(QQ)

        if b.base_ring() != QQ:
            #b = vector(QQ, [QQ(bi) for bi in b]);
            b.change_ring(QQ)

        ieqs_list = []
        for i in range(A.nrows()):
            ieqs_list.append(list(-A.row(i)))  #change in sign, necessary since Polyhedron receives Ax+b>=0
            ieqs_list[i].insert(0,b[i])

        P = Polyhedron(ieqs = ieqs_list, base_ring=QQ, ambient_dim=A.ncols(), backend = 'ppl')

    else:
        raise ValueError('Base ring not supported. Try with RDF or QQ.')

    return P
        
def chebyshev_center(P=None, A=None, b=None):
    r"""Compute Chebyshev center of polytope.

    The Chebyshev center of a polytope is the center of the largest hypersphere enclosed by the polytope.

    INPUT:

    * "A, b" - Matrix and vector representing the polyhedron, as Ax <= b.

    * "P" - Polyhedron object.

    OUTPUT:

    * "cheby_center" - the Chebyshev center, as a vector. The base_ring is preserved.

    """

    # parse input
    got_P, got_Ab = False, False;
    if (P is not None):
        if (A is None) and (b is None):
            got_P = True
        elif (A is not None) and (b is None):
            b, A = A, P; P = [];
            got_Ab = True
    else:
        got_Ab = True if (A is not None and b is not None) else False

    if got_Ab or got_P:
        if got_P:
            [A, b] = polyhedron_to_Hrep(P)

        base_ring = A.base_ring()
        p = MixedIntegerLinearProgram (maximization = True)
        x = p.new_variable ()
        r = p.new_variable ()
        n = A.nrows ()
        m = A.ncols ()
        if not n == b.length () :
            return []
        for i in range (0, n) :
            v = A.row (i)
            norm = sqrt (v.dot_product (v))
            p.add_constraint (sum ([v[j]*x[j] for j in range (0, m)]) + norm * r[0] <= b[i])
        f = sum ([0*x[i] for i in range (0, m)]) + 1 * r[0]
        p.set_objective(f)
        p.solve()
        cheby_center = [base_ring(p.get_values (x[i])) for i in range (0, m)]
        return vector(cheby_center)
    else:
        raise ValueError('The input should be either as a Polyhedron, P, or as matrices, [A, b].')    
    
def radius(P):
    r"""Compute maximum norm of any element in a polyhedron (in the sup norm).

    It is defined as `max_{x in P} \Vert x \Vert|_inf`. It can be computed with support functions as 
    `max_{i=1,...,n} max{|rho(P, ei)|, |rho(P,-ei)|}``, 
    where `rho(P, ei)`` is the support function of `P` evaluated at `ei`, and `ei` is the i-th canonical vector in `\\R^n`.

    INPUT:

    * "P" - an object of class Polyhedron. It can also be given as [A, b] with A and b matrices, assuming Ax <= b.

    OUTPUT:

    * "snorm" - the value of the max norm of any element of P, in the sup-norm.

    TO-DO:

    To use *args so that it works both with polyhedron_sup_norm(A, b) and with polyhedron_sup_norm(P) (depending on the number of the arguments). 
    The difference with mult-methods is that they check also for the type of the arguments.

    """

    if (type(P) == list):

        A = P[0]; b = P[1];
        # obtain dimension of the ambient space
        n = A.ncols();

        r = 0
        for i in range(n):
            # generate canonical direction
            d = zero_vector(RDF,n)
            d[i] = 1
            aux_sf = abs(supp_fun_polyhedron([A, b], d))
            if (aux_sf >= r):
                r = aux_sf;

            # change sign
            d[i] = -1
            aux_sf = abs(supp_fun_polyhedron([A, b], d))
            if (aux_sf >= r):
                r = aux_sf;
        snorm = r
        return snorm    
        
def supp_fun_polyhedron(P, d, verbose = 0, return_xopt = False, solver = 'GLPK'):
    r"""Compute support function of a convex polytope.

    It is defined as max_{x in P} <x,d> , where d is an input vector.

    INPUT:

    * "P" - an object of class Polyhedron. It can also be given as [A, b] with A and b matrices, assuming Ax <= b.

    * "d" - a vector (or list) where the support function is evaluated.

    * "verbose" - (default: 0) If 1, print the status of the LP.

    * "solver" - (default: 'GLPK') the LP solver used.

    * "return_xopt" - (default: False) If True, the optimal point is returned, and sf = [oval, opt].

    OUTPUT:

    * "sf" - the value of the support function.

    EXAMPLES::

    sage: P = BoxInfty([1,2,3], 1); P
    A 3-dimensional polyhedron in QQ^3 defined as the convex hull of 8 vertices

    sage: supp_fun_polyhedron(P, [1,1,1], return_xopt=True)
    (9.0, {0: 2.0, 1: 3.0, 2: 4.0})
    
    TO-DO::

    - Test with more solvers (GLPK, Gurobi, ...)

    NOTES::

    - The possibility of giving the input polytope as [A, b] instead of a 
    polyhedron P is useful in cases when the dimensions are high  (in practice, 
    more than 30, but it depends on the particular system -number of 
    constraints- as well). 
    
    - In fact, it is often the case that the data is given in matrix format (A, b), 
    hence it might be preferable to avoid the overhead of  building the Polyhedra, 
    if our intention is solely to make computations that can be performed on 
    the matrices A and b directly. The improve in speed is quite considerable.

    - If a different solver is given, it should be installed properly.

    sage: supp_fun_polyhedron(P, [1,1,1], solver='Gurobi')
    9.0
    """

    # avoid formulating the LP if P = []
    if P.is_empty():
        return 0

    s_LP = MixedIntegerLinearProgram(maximization=True, solver = solver)
    x = s_LP.new_variable(integer=False, nonnegative=False)

    # objective function
    obj = sum(d[i]*x[i] for i in range(len(d)))
    s_LP.set_objective(obj)

    if (type(P) == list):
        A = P[0]; b = P[1];

    else: #assuming some form of Polyhedra
        base_ring = P.base_ring()
        # extract the constraints from P
        m = len(P.Hrepresentation())
        n = len(vector( P.Hrepresentation()[0] ))-1
        b = vector(base_ring, m)
        A = matrix(base_ring, m, n)
        P_gen = P.Hrep_generator();
        i=0
        for pigen in P_gen:
            pi_vec = pigen.vector()
            A.set_row(i, -pi_vec[1:len(pi_vec)])
            b[i] = pi_vec[0]
            i+=1;

    s_LP.add_constraint(A * x <= b);

    if (verbose):
        print '**** Solve LP  ****'
        s_LP.show()

    oval = s_LP.solve()
    xopt = s_LP.get_values(x);

    if (verbose):
        print 'Objective Value:', oval
        for i, v in xopt.iteritems():
            print 'x_%s = %f' % (i, v)
        print '\n'

    if (return_xopt == True):
        return oval, xopt
    else:
        return oval     
        
def BoxInfty(lengths=None, center=None, radius=None, base_ring=QQ, return_HSpaceRep=False):
    r"""Generate a box (hyper-rectangle) in the supremum norm.

    It can be constructed from its center and radius, in which case it is a box. It can also be constructed giving the lengths of the sides, in which case it is an hyper-rectangle. In all cases, it is defined as the Cartesian product of intervals.

    INPUT:

    * "args" - Available options are:

        * by center and radius:

            * "center" - a vector (or a list) containing the coordinates of the center of the ball.

            * "radius" - a number representing the radius of the ball.

        * by lengths:

            * "lenghts" - a list of tuples containing the length of each side with respect to the coordinate axes, in the form [(min_x1, max_x1), ..., (min_xn, max_xn)]

    * "base_ring" - (default: QQ) base ring passed to the Polyhedron constructor. Valid choices are:

        * "'QQ'": rational

        * "'RDF'": real double field

    * "return_HSpaceRep" - (default: False) If True, it does not construct the Polyhedron P, and returns instead the pairs [A, b] corresponding to P in half-space representation, as Ax <= b.

    OUTPUT:

    * "P" - a Polyhedron object. If the flag return_HSpaceRep=True, it is returned as [A, b] with A and b matrices, assuming Ax <= b.

    EXAMPLES:

    sage: P = BoxInfty([1,2,3], 1); P
    A 3-dimensional polyhedron in QQ^3 defined as the convex hull of 8 vertices

    sage: P.plot(aspect_ratio=1)    # not tested (plot)

    NOTES::

    - The possibility to output in matrix form [A, b] is especially interesting 
    for more than 15 variable systems.
    """
    # Guess input
    got_lengths, got_center_and_radius = False, False;
    if (lengths is not None):
        if (center is None) and (radius is None):
            got_lengths = True
        elif (center is not None) and (radius is None):
            radius = center; center = lengths; lengths = [];
            got_center_and_radius = True
    else:
        got_center_and_radius = True if (center is not None and radius is not None) else False

    # Given center and radius
    if got_center_and_radius:

        # cast (optional)
        center = [base_ring(xi) for xi in center]
        radius = base_ring(radius)

        ndim = len(center)
        A = matrix(base_ring, 2*ndim, ndim);
        b = vector(base_ring,2*ndim)

        count = 0
        for i in range(ndim):
            diri = zero_vector(base_ring,ndim)
            diri[i] = 1

            # external bound
            A.set_row(count, diri)
            b[count] = center[i] + radius
            count += 1

            # internal bound
            A.set_row(count, -diri)
            b[count] = -(center[i] - radius)
            count += 1


    # Given the length of each side as tuples (min, max)
    elif got_lengths:

        # clean up the argument and cast
        lengths = _make_listlist(lengths)
        lengths = [[base_ring(xi) for xi in l] for l in lengths]

        ndim = len(lengths)
        A = matrix(base_ring, 2*ndim, ndim)
        b = vector(base_ring, 2*ndim)

        count = 0
        for i in range(ndim):
            diri = zero_vector(base_ring, ndim)
            diri[i] = 1

            # external bound
            A.set_row(count, diri)
            b[count] = lengths[i][1]
            count += 1

            # internal bound
            A.set_row(count, -diri)
            b[count] = -(lengths[i][0])
            count += 1

    else:
        raise ValueError('You should specify either center and radius or length of the sides.')

    if not return_HSpaceRep:
        P = polyhedron_from_Hrep(A, b, base_ring)
        return P
    else:
        return [A, b]           