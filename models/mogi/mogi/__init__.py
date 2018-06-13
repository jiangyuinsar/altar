# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
#
# (c) 2013-2018 parasim inc
# (c) 2010-2018 california institute of technology
# all rights reserved
#

# the package
import altar


# implementations
@altar.foundry(implements=altar.models.model, tip="a multi-parameter Mogi model")
def mogi():
    # grab the factory
    from .Mogi import Mogi as mogi
    # attach its docstring
    __doc__ = mogi.__doc__
    # and return it
    return mogi


# end of file