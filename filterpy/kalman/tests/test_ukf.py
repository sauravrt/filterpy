# -*- coding: utf-8 -*-

"""Copyright 2014 Roger R Labbe Jr.

filterpy library.
http://github.com/rlabbe/filterpy

This is licensed under an MIT license. See the readme.MD file
for more information.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import matplotlib.pyplot as plt
import numpy.random as random
from numpy.random import randn
import math
import numpy as np
from filterpy.kalman import UnscentedKalmanFilter as UKF, JulierPoints
from filterpy.common import stats

DO_PLOT = False


def test_sigma_plot():
    """ Test to make sure sigma's correctly mirror the shape and orientation
    of the covariance array."""

    x = np.array([[1, 2]])
    P = np.array([[2, 1.2],
                  [1.2, 2]])
    kappa = .1

    # if kappa is larger, than points shoudld be closer together
    jp0 = JulierPoints(2, kappa)
    jp1 = JulierPoints(2, kappa*1000)

    Xi0 = jp0.sigma_points (x, P)
    Xi1 = jp1.sigma_points (x, P)

    assert max(Xi1[:,0]) > max(Xi0[:,0])
    assert max(Xi1[:,1]) > max(Xi0[:,1])

    if DO_PLOT:
        plt.figure()
        for i in range(Xi0.shape[0]):
            plt.scatter((Xi0[i,0]-x[0, 0])*jp0.Wm[i] + x[0, 0],
                        (Xi0[i,1]-x[0, 1])*jp0.Wm[i] + x[0, 1],
                         color='blue')

        for i in range(Xi1.shape[0]):
            plt.scatter((Xi1[i, 0]-x[0, 0]) * jp1.Wm[i] + x[0,0],
                        (Xi1[i, 1]-x[0, 1]) * jp1.Wm[i] + x[0,1],
                         color='green')

        stats.plot_covariance_ellipse([1, 2], P)


def test_sigma_points_1D():
    """ tests passing 1D data into sigma_points"""
    jp = JulierPoints(1, 0.)
    assert jp.Wc.all() == jp.Wm.all()

    mean = 5
    cov = 9

    Xi = jp.sigma_points (mean, cov)
    xm, ucov = UKF.unscented_transform(Xi, jp.Wm, jp.Wc, 0)

    # sum of weights*sigma points should be the original mean
    m = 0.0
    for x,w in zip(Xi, jp.Wm):
        m += x*w

    assert abs(m-mean) < 1.e-12
    assert abs(xm[0] - mean) < 1.e-12
    assert abs(ucov[0,0]-cov) < 1.e-12

    assert Xi.shape == (3,1)
    assert len(jp.Wc) == 3


class RadarSim(object):
    def __init__(self, dt):
        self.x = 0
        self.dt = dt

    def get_range(self):
        vel = 100  + 5*randn()
        alt = 1000 + 10*randn()
        self.x += vel*self.dt

        v = self.x * 0.05*randn()
        rng = (self.x**2 + alt**2)**.5 + v
        return rng


def test_radar():
    def fx(x, dt):
        A = np.eye(3) + dt * np.array ([[0, 1, 0],
                                        [0, 0, 0],
                                        [0, 0, 0]])
        return A.dot(x)

    def hx(x):
        return np.sqrt (x[0]**2 + x[2]**2)

    dt = 0.05

    jp = JulierPoints(3,0)

    kf = UKF(3, 1, dt, jp)

    kf.Q *= 0.01
    kf.R = 10
    kf.x = np.array([0., 90., 1100.])
    kf.P *= 100.
    radar = RadarSim(dt)

    t = np.arange(0,20+dt, dt)

    n = len(t)

    xs = np.zeros((n,3))

    random.seed(200)
    rs = []
    #xs = []
    for i in range(len(t)):
        r = radar.get_range()
        #r = GetRadar(dt)
        kf.predict(fx)
        kf.update(r, hx)

        xs[i,:] = kf.x
        rs.append(r)

    if DO_PLOT:
        print(xs[:,0].shape)

        plt.figure()
        plt.subplot(311)
        plt.plot(t, xs[:,0])
        plt.subplot(312)
        plt.plot(t, xs[:,1])
        plt.subplot(313)

        plt.plot(t, xs[:,2])


if __name__ == "__main__":

    test_sigma_points_1D()


    DO_PLOT = True

    '''test_1D_sigma_points()
    #plot_sigma_test ()

    x = np.array([[1,2]])
    P = np.array([[2, 1.2],
                  [1.2, 2]])
    kappa = .1

    xi,w = sigma_points (x,P,kappa)
    xm, cov = unscented_transform(xi, w)'''
    test_radar()
    test_sigma_plot()



    #print('xi=\n',Xi)
    """
    xm, cov = unscented_transform(Xi, W)
    print(xm)
    print(cov)"""
#    sigma_points ([5,2],9*np.eye(2), 2)
