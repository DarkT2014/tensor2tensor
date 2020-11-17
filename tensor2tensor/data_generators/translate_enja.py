# coding=utf-8
# Copyright 2020 The Tensor2Tensor Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Data generators for translation data-sets."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from tensor2tensor.data_generators import generator_utils
from tensor2tensor.data_generators import problem
from tensor2tensor.data_generators import text_encoder
from tensor2tensor.data_generators import text_problems
from tensor2tensor.data_generators import translate
from tensor2tensor.utils import registry

import tensorflow.compat.v1 as tf


# End-of-sentence marker.
EOS = text_encoder.EOS_ID

# The KFTT is a task for the evaluation and development of
# Japanese-English machine translation systems.
#
# http://www.phontron.com/kftt/
# Wikipedia articles about Kyoto manually translated by NICT.
# ja files already tokenized
# around 330k lines
_KFTT_TRAIN_DATASETS = [[
    "http://www.phontron.com/kftt/download/kftt-data-1.0.tar.gz", [
        "kftt-data-1.0/data/tok/kyoto-train.cln.en",
        "kftt-data-1.0/data/tok/kyoto-train.cln.ja"
    ]
]]

# Test set from KFTT. 1160 lines
_KFTT_TEST_DATASETS = [[
    "http://www.phontron.com/kftt/download/kftt-data-1.0.tar.gz", [
        "kftt-data-1.0/data/tok/kyoto-test.cln.en",
        "kftt-data-1.0/data/tok/kyoto-test.cln.ja"
    ]
]]

# JParaCrawl ： 10,120,013 lines.
# Visit source website to download manually:
# http://www.kecl.ntt.co.jp/icl/lirg/jparacrawl/

_JPC_TRAIN_DATASETS = [[
    "http://www.kecl.ntt.co.jp/icl/lirg/jparacrawl/release/2.0/bitext/en-ja.tar"
    ".gz", ["en-ja/en-ja.bicleaner05.txt.en", "en-ja/en-ja.bicleaner05.txt.ja"]
]]

# # CWMT corpus
# # Visit source website to download manually:
# # http://nlp.nju.edu.cn/cwmt-wmt/
# #
# # casia2015: 1,050,000 lines
# # casict2015: 2,036,833 lines
# # datum2015:  1,000,003 lines
# # datum2017: 1,999,968 lines
# # NEU2017:  2,000,000 lines
# # total: appromirate 8,085,000
# #
# # NOTE: You need to register to download dataset from official source
# # place into tmp directory e.g. /tmp/t2t_datagen/dataset.tgz

# _CWMT_TRAIN_DATASETS = [[
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/casia2015/casia2015_en.txt", "cwmt/casia2015/casia2015_ch.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/casict2015/casict2015_en.txt", "cwmt/casict2015/casict2015_ch.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/neu2017/NEU_en.txt", "cwmt/neu2017/NEU_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2015/datum_en.txt", "cwmt/datum2015/datum_ch.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book1_en.txt", "cwmt/datum2017/Book1_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book2_en.txt", "cwmt/datum2017/Book2_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book3_en.txt", "cwmt/datum2017/Book3_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book4_en.txt", "cwmt/datum2017/Book4_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book5_en.txt", "cwmt/datum2017/Book5_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book6_en.txt", "cwmt/datum2017/Book6_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book7_en.txt", "cwmt/datum2017/Book7_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book8_en.txt", "cwmt/datum2017/Book8_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book9_en.txt", "cwmt/datum2017/Book9_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book10_en.txt", "cwmt/datum2017/Book10_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book11_en.txt", "cwmt/datum2017/Book11_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book12_en.txt", "cwmt/datum2017/Book12_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book13_en.txt", "cwmt/datum2017/Book13_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book14_en.txt", "cwmt/datum2017/Book14_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book15_en.txt", "cwmt/datum2017/Book15_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book16_en.txt", "cwmt/datum2017/Book16_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book17_en.txt", "cwmt/datum2017/Book17_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book18_en.txt", "cwmt/datum2017/Book18_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book19_en.txt", "cwmt/datum2017/Book19_cn.txt"]
# ], [
#     "https://s3-us-west-2.amazonaws.com/twairball.wmt17.zh-en/cwmt.tgz",
#     ["cwmt/datum2017/Book20_en.txt", "cwmt/datum2017/Book20_cn.txt"]
# ]]

_JESC_TRAIN_DATASETS = [[
    "https://nlp.stanford.edu/projects/jesc/data/raw.tar.gz",
    ["raw/raw.en", "raw/raw.ja"]
]]


def get_filename(dataset):
  return dataset[0][0].split("/")[-1]


@registry.register_problem
class TranslateEnjaWmt32k(translate.TranslateProblem):
  """Problem spec for WMT En-Zh translation.

  Attempts to use full training dataset, which needs website
  registration and downloaded manually from official sources:

  CWMT:
    - http://nlp.nju.edu.cn/cwmt-wmt/
    - Website contains instructions for FTP server access.
    - You'll need to download CASIA, CASICT, DATUM2015, DATUM2017,
        NEU datasets

  UN Parallel Corpus:
    - https://conferences.unite.un.org/UNCorpus
    - You'll need to register your to download the dataset.

  NOTE: place into tmp directory e.g. /tmp/t2t_datagen/dataset.tgz
  """

  @property
  def approx_vocab_size(self):
    return 2**15  # 32k

  @property
  def source_vocab_name(self):
    return "%s.en" % self.vocab_filename

  @property
  def target_vocab_name(self):
    return "%s.ja" % self.vocab_filename

  def get_training_dataset(self, tmp_dir):
    """UN Parallel Corpus and CWMT Corpus need to be downloaded manually.

    Append to training dataset if available

    Args:
      tmp_dir: path to temporary dir with the data in it.

    Returns:
      paths
    """
    full_dataset = _KFTT_TEST_DATASETS
    # for dataset in [_CWMT_TRAIN_DATASETS, _UN_TRAIN_DATASETS]:

    for dataset in [_JESC_TRAIN_DATASETS, _JPC_TRAIN_DATASETS]:
      filename = get_filename(dataset)
      tmp_filepath = os.path.join(tmp_dir, filename)
      if tf.gfile.Exists(tmp_filepath):
        full_dataset += dataset
      else:
        tf.logging.info("[TranslateEnjaWmt] dataset incomplete, you need to "
                        "manually download %s" % filename)
    return full_dataset

  def generate_encoded_samples(self, data_dir, tmp_dir, dataset_split):
    train = dataset_split == problem.DatasetSplit.TRAIN
    train_dataset = self.get_training_dataset(tmp_dir)
    datasets = train_dataset if train else _KFTT_TEST_DATASETS
    source_datasets = [[item[0], [item[1][0]]] for item in train_dataset]
    target_datasets = [[item[0], [item[1][1]]] for item in train_dataset]
    source_vocab = generator_utils.get_or_generate_vocab(
        data_dir,
        tmp_dir,
        self.source_vocab_name,
        self.approx_vocab_size,
        source_datasets,
        file_byte_budget=1e8,
        max_subtoken_length=self.max_subtoken_length)
    target_vocab = generator_utils.get_or_generate_vocab(
        data_dir,
        tmp_dir,
        self.target_vocab_name,
        self.approx_vocab_size,
        target_datasets,
        file_byte_budget=1e8,
        max_subtoken_length=self.max_subtoken_length)
    tag = "train" if train else "dev"
    filename_base = "wmt_enja_%sk_tok_%s" % (self.approx_vocab_size, tag)
    data_path = translate.compile_data(tmp_dir, datasets, filename_base)
    return text_problems.text2text_generate_encoded(
        text_problems.text2text_txt_iterator(data_path + ".lang1",
                                             data_path + ".lang2"),
        source_vocab, target_vocab)

  def feature_encoders(self, data_dir):
    source_vocab_filename = os.path.join(data_dir, self.source_vocab_name)
    target_vocab_filename = os.path.join(data_dir, self.target_vocab_name)
    source_token = text_encoder.SubwordTextEncoder(source_vocab_filename)
    target_token = text_encoder.SubwordTextEncoder(target_vocab_filename)
    return {
        "inputs": source_token,
        "targets": target_token,
    }


@registry.register_problem
class TranslateEnjaWmt8k(TranslateEnjaWmt32k):
  """Problem spec for WMT En-Zh translation.

  This is far from being the real WMT17 task - only toyset here
  """

  @property
  def approx_vocab_size(self):
    return 2**13  # 8192

  @property
  def dataset_splits(self):
    return [
        {
            "split": problem.DatasetSplit.TRAIN,
            "shards": 10,  # this is a small dataset
        },
        {
            "split": problem.DatasetSplit.EVAL,
            "shards": 1,
        }
    ]

  def get_training_dataset(self, tmp_dir):
    """Uses only News Commentary Dataset for training."""
    # return _NC_TRAIN_DATASETS
    return _KFTT_TRAIN_DATASETS
