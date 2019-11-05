from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os

import tensorflow as tf

class NADEGraph(object):
  """Model for predicting autofills given context."""

  def __init__(self,
               is_training,
               hparams,
               placeholders=None,
               direct_inputs=None,
               use_placeholders=True):
    self.hparams = hparams
    self.batch_size = hparams.batch_size
    self.num_pitches = hparams.num_pitches
    self.num_instruments = hparams.num_instruments
    self.is_training = is_training
    self.placeholders = placeholders
    self._direct_inputs = direct_inputs
    self._use_placeholders = use_placeholders
    self.hiddens = []
    self.popstats_by_batchstat = collections.OrderedDict()
    self.build()

  @property
  def use_placeholders(self):
    return self._use_placeholders

  @use_placeholders.setter
  def use_placeholders(self, use_placeholders):
    self._use_placeholders = use_placeholders

  @property
  def inputs(self):
    if self.use_placeholders:
      return self.placeholders
    else:
      return self.direct_inputs

  @property
  def direct_inputs(self):
    return self._direct_inputs

  @direct_inputs.setter
  def direct_inputs(self, direct_inputs):
    if set(direct_inputs.keys()) != set(self.placeholders.keys()):
      raise AttributeError('Need to have pianorolls, masks, lengths.')
    self._direct_inputs = direct_inputs

  @property
  def pianorolls(self):
    return self.inputs['pianorolls']

  @property
  def masks(self):
    return self.inputs['masks']

  @property
  def lengths(self):
    return self.inputs['lengths']




NADEGraph(is_training=True, hparams = 1)