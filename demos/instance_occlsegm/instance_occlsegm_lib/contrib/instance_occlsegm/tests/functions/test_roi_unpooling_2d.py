import unittest

import numpy

import chainer
from chainer import cuda
from chainer import gradient_check
from chainer import testing
from chainer.testing import attr
from chainer.testing import condition

from ... import functions


class TestROIUnpooling2D(unittest.TestCase):

    def setUp(self):
        n_channels = 3
        self.rois = numpy.array([
            [0, 1, 1, 6, 6],
            [2, 6, 2, 7, 11],
            [1, 3, 1, 5, 10],
            [0, 3, 3, 3, 3]
        ], dtype=numpy.float32)
        n_rois = self.rois.shape[0]
        pooledh, pooledw = 5, 7
        self.x = numpy.arange(
            n_rois * n_channels * pooledh * pooledw,
            dtype=numpy.float32,
        ).reshape((n_rois, n_channels, pooledh, pooledw))
        numpy.random.shuffle(self.x)
        self.x = 2 * self.x / self.x.size - 1
        self.outb = 3
        self.outh, self.outw = 5, 7
        self.spatial_scale = 0.6
        self.gy = numpy.random.uniform(
            -1, 1, (self.outb, n_channels,
                    self.outh, self.outw)).astype(numpy.float32)
        self.check_backward_options = {'atol': 5e-4, 'rtol': 5e-3}

    def check_forward(self, x_data, roi_data):
        x = chainer.Variable(x_data)
        rois = chainer.Variable(roi_data)
        y = functions.roi_unpooling_2d(
            x, rois, outb=self.outb, outh=self.outh, outw=self.outw,
            spatial_scale=self.spatial_scale)
        self.assertEqual(y.data.dtype, numpy.float32)
        y_data = cuda.to_cpu(y.data)

        self.assertEqual(self.gy.shape, y_data.shape)

    @condition.retry(3)
    def test_forward_cpu(self):
        self.check_forward(self.x, self.rois)

    @attr.gpu
    @condition.retry(3)
    def test_forward_gpu(self):
        self.check_forward(cuda.to_gpu(self.x), cuda.to_gpu(self.rois))

    @attr.gpu
    @condition.retry(3)
    def test_forward_cpu_gpu_equal(self):
        # cpu
        x_cpu = chainer.Variable(self.x)
        rois_cpu = chainer.Variable(self.rois)
        y_cpu = functions.roi_unpooling_2d(
            x_cpu, rois_cpu, outb=self.outb, outh=self.outh, outw=self.outw,
            spatial_scale=self.spatial_scale)

        # gpu
        x_gpu = chainer.Variable(cuda.to_gpu(self.x))
        rois_gpu = chainer.Variable(cuda.to_gpu(self.rois))
        y_gpu = functions.roi_unpooling_2d(
            x_gpu, rois_gpu, outb=self.outb, outh=self.outh, outw=self.outw,
            spatial_scale=self.spatial_scale)
        testing.assert_allclose(y_cpu.data, cuda.to_cpu(y_gpu.data))

    def check_backward(self, x_data, roi_data, y_grad):
        gradient_check.check_backward(
            functions.ROIUnpooling2D(
                outb=self.outb, outh=self.outh, outw=self.outw,
                spatial_scale=self.spatial_scale),
            (x_data, roi_data), y_grad, no_grads=[False, True],
            **self.check_backward_options)

    @condition.retry(3)
    def test_backward_cpu(self):
        self.check_backward(self.x, self.rois, self.gy)

    @attr.gpu
    @condition.retry(3)
    def test_backward_gpu(self):
        self.check_backward(cuda.to_gpu(self.x), cuda.to_gpu(self.rois),
                            cuda.to_gpu(self.gy))


testing.run_module(__name__, __file__)
