# -*- python -*-
# -*- coding: utf-8 -*-
#
# michael a.g. aïvázis <michael.aivazis@para-sim.com>
#
# (c) 2013-2019 parasim inc
# (c) 2010-2019 california institute of technology
# all rights reserved
#


# externals
import altar
# the pure python implementation of the Mogi source
from altar.models.mogi.ext import libcudamogi


# declaration
class CUDA:
    """
    A strategy for computing the data log likelihood that is written in pure python
    """

    # interface
    def initialize(self, application, model):
        """
        Initialize the strategy with {model} information
        """
        # get the number of observations
        observations = model.observations
        # the locations on the ground where the observations were made
        locations = model.points
        # the observed displacements
        displacements = model.d
        # the array with the lines of sight to the observation locations
        los = model.los
        # and the data set id for each observation
        oid = model.oid

        # get the number of parameters
        nParameters = model.parameters
        # the number of samples
        nSamples = application.job.chains
        # and the number of observations
        nObservations = model.observations

        # build the calculator
        source = libcudamogi.newSource(nParameters, nSamples, nObservations, model.nu)

        # attach the coordinates of the observation points
        libcudamogi.locations(source, locations)
        # attach the observed displacements
        libcudamogi.data(source, displacements.data)
        # attach the LOS vectors
        libcudamogi.los(source, los.data)
        # attach the map of observations to their set
        libcudamogi.oid(source, oid)
        # inform the source about the parameter layout; assumes contiguous parameter sets
        libcudamogi.layout(source, model.xIdx, model.dIdx, model.sIdx, model.offsetIdx)

        # if all went well, attach the calculator
        self.source = source

        # nothing to do
        return self


    def dataLikelihood(self, model, step):
        """
        Fill {step.data} with the likelihoods of the samples in {step.theta} given the available
        data.
        """
        # grab my calculator
        source = self.source
        # compute the portion of the sample that belongs to this model
        θ = model.restrict(theta=step.theta)
        # allocate a matrix to hold the predicted displacements
        predicted = altar.matrix(shape=(step.samples, model.observations))

        # compute the residuals (in place)
        libcudamogi.residuals(source, θ.capsule, predicted.data)

        # get the norm
        norm = model.norm
        # the inverse of the data covariance matrix
        cd_inv = model.cd_inv
        # the normalization
        normalization = model.normalization
        # and the data likelihood vector
        dataLLK = step.data

        # find out how many samples in the set
        samples = θ.rows
        # go through the samples
        for sample in range(samples):
            # get the residuals
            residuals = predicted.getRow(sample)
            # compute the norm, and normalize it
            llk = normalization - norm.eval(v=residuals, sigma_inv=cd_inv) / 2
            # store it
            dataLLK[sample] = llk

        # all done
        return self


    # private data
    source = None


# end of file
