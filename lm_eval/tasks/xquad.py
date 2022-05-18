"""
On the cross-lingual transferability of monolingual representations
https://arxiv.org/abs/1910.11856

XQuAD (Cross-lingual Question Answering Dataset) is a benchmark dataset 
for evaluating cross-lingual question answering performance. The dataset 
consists of a subset of 240 paragraphs and 1190 question-answer pairs from 
the development set of SQuAD v1.1 (Rajpurkar et al., 2016) together with 
their professional translations into ten languages: Spanish, German, Greek, 
Russian, Turkish, Arabic, Vietnamese, Thai, Chinese, and Hindi. 
Consequently, the dataset is entirely parallel across 11 languages.

Homepage: https://github.com/deepmind/xquad
"""
import datasets
from math import exp
from lm_eval.base import rf, Task
from functools import partial
from packaging import version
from lm_eval.base import PromptSourceTask


_CITATION = """
@article{Artetxe:etal:2019,
      author    = {Mikel Artetxe and Sebastian Ruder and Dani Yogatama},
      title     = {On the cross-lingual transferability of monolingual representations},
      journal   = {CoRR},
      volume    = {abs/1910.11856},
      year      = {2019},
      archivePrefix = {arXiv},
      eprint    = {1910.11856}
}
"""


def _squad_metric(predictions, references):
    squad_metric = datasets.load_metric("squad_v2")
    return squad_metric.compute(predictions=predictions, references=references)


def _squad_agg(key, items):
    predictions, references = zip(*items)
    return _squad_metric(predictions=predictions, references=references)[key]


class xquad_en(PromptSourceTask):
    VERSION = 1
    DATASET_PATH = "xquad"
    DATASET_NAME = "xquad.en"

    # HF changed squad on us so we have to make sure we aren't running the old one
    assert version.parse(datasets.__version__) >= version.parse("1.11.0"), "datasets v1.11.0 or later required for SQuAD"

    def has_training_docs(self):
        return False

    def has_validation_docs(self):
        return True

    def has_test_docs(self):
        return False

    def training_docs(self):
        return self.dataset["train"]

    def validation_docs(self):
        return self.dataset["validation"]

    def construct_requests(self, doc, ctx, args):
        """Uses RequestFactory to construct Requests and returns an iterable of
        Requests which will be sent to the LM.

        :param doc:
            The document as returned from training_docs, validation_docs, or test_docs.
        :param ctx: str
            The context string, generated by fewshot_context. This includes the natural
            language description, as well as the few shot examples, and the question
            part of the document for `doc`.
        :param args: dict
            The specifics of the context, including number of few shots.
        """

        request_args = {
            "stopping_criteria": self.stopping_criteria(),
            "max_generation_length": self.max_generation_length(),
            "num_fewshot": args["num_fewshot"],
        }

        cont_request = rf.greedy_until(ctx, request_args)
        is_unanswerable = rf.loglikelihood(ctx, " " + "unanswerable")
        
        return cont_request,is_unanswerable



    def process_results(self, doc, results):
        """Take a single document and the LM results and evaluates, returning a 
        dict where keys are the names of submetrics and values are the values of 
        the metric for that one document

        :param doc:
            The document as returned from training_docs, validation_docs, or test_docs.
        :param results:
            The results of the requests created in construct_requests.
        """

        pred, (logprob_unanswerable, _) = results
        no_answer_probability = exp(logprob_unanswerable)
        
        predictions = {
            'id': doc['id'],
            'prediction_text': pred,
            'no_answer_probability': no_answer_probability,
        }

        references = {
            'id': doc['id'],
            'answers': doc['answers'],
        }

        if self.save_examples:
            example = {
                "pred": pred,
                "target": doc['answers'],
            }
        return { 
            'exact': (predictions, references), # Exact match (the normalized answer exactly match the gold answer)
            'f1': (predictions, references), #  The F-score of predicted tokens versus the gold answer
            'HasAns_exact': (predictions, references), # Exact match (the normalized answer exactly match the gold answer)
            'HasAns_f1': (predictions, references), # The F-score of predicted tokens versus the gold answer
            'NoAns_exact': (predictions, references), # Exact match (the normalized answer exactly match the gold answer)
            'NoAns_f1': (predictions, references), # The F-score of predicted tokens versus the gold answer
            'best_exact': (predictions, references), # Best exact match (with varying threshold)
            'best_f1': (predictions, references), # Best F1 (with varying threshold)
        }, example

    def aggregation(self):
        """
        :returns: {str: [float] -> float}
            A dictionary where keys are the names of submetrics and values are 
            functions that aggregate a list of metrics
        """
        return { 
            'exact': partial(_squad_agg, 'exact'), # Exact match (the normalized answer exactly match the gold answer)
            'f1': partial(_squad_agg, 'f1'), #  The F-score of predicted tokens versus the gold answer
            'HasAns_exact': partial(_squad_agg, 'HasAns_exact'), # Exact match (the normalized answer exactly match the gold answer)
            'HasAns_f1': partial(_squad_agg, 'HasAns_f1'), # The F-score of predicted tokens versus the gold answer
            'NoAns_exact': partial(_squad_agg, 'NoAns_exact'), # Exact match (the normalized answer exactly match the gold answer)
            'NoAns_f1': partial(_squad_agg, 'NoAns_f1'), # The F-score of predicted tokens versus the gold answer
            'best_exact': partial(_squad_agg, 'best_exact'), # Best exact match (with varying threshold)
            'best_f1': partial(_squad_agg, 'best_f1'), # Best F1 (with varying threshold)
        }

    def higher_is_better(self):
        """
        :returns: {str: bool}
            A dictionary where keys are the names of submetrics and values are 
            whether a higher value of the submetric is better
        """
        return { 
            'exact': True, # Exact match (the normalized answer exactly match the gold answer)
            'f1': True, #  The F-score of predicted tokens versus the gold answer
            'HasAns_exact': True, # Exact match (the normalized answer exactly match the gold answer)
            'HasAns_f1': True, # The F-score of predicted tokens versus the gold answer
            'NoAns_exact': True, # Exact match (the normalized answer exactly match the gold answer)
            'NoAns_f1': True, # The F-score of predicted tokens versus the gold answer
            'best_exact': True, # Best exact match (with varying threshold)
            'best_f1': True, # Best F1 (with varying threshold)
        }



class xquad_ar(PromptSourceTask):
    VERSION = 1
    DATASET_PATH = "xquad"
    DATASET_NAME = "xquad.ar"

    # HF changed squad on us so we have to make sure we aren't running the old one
    assert version.parse(datasets.__version__) >= version.parse("1.11.0"), "datasets v1.11.0 or later required for SQuAD"

    def has_training_docs(self):
        return False

    def has_validation_docs(self):
        return True

    def has_test_docs(self):
        return False

    def training_docs(self):
        return self.dataset["train"]

    def validation_docs(self):
        return self.dataset["validation"]

    def construct_requests(self, doc, ctx, args):
        """Uses RequestFactory to construct Requests and returns an iterable of
        Requests which will be sent to the LM.

        :param doc:
            The document as returned from training_docs, validation_docs, or test_docs.
        :param ctx: str
            The context string, generated by fewshot_context. This includes the natural
            language description, as well as the few shot examples, and the question
            part of the document for `doc`.
        :param args: dict
            The specifics of the context, including number of few shots.
        """

        request_args = {
            "stopping_criteria": self.stopping_criteria(),
            "max_generation_length": self.max_generation_length(),
            "num_fewshot": args["num_fewshot"],
        }

        cont_request = rf.greedy_until(ctx, request_args)
        is_unanswerable = rf.loglikelihood(ctx, " " + "unanswerable")
        
        return cont_request,is_unanswerable



    def process_results(self, doc, results):
        """Take a single document and the LM results and evaluates, returning a 
        dict where keys are the names of submetrics and values are the values of 
        the metric for that one document

        :param doc:
            The document as returned from training_docs, validation_docs, or test_docs.
        :param results:
            The results of the requests created in construct_requests.
        """

        pred, (logprob_unanswerable, _) = results
        no_answer_probability = exp(logprob_unanswerable)
        
        predictions = {
            'id': doc['id'],
            'prediction_text': pred,
            'no_answer_probability': no_answer_probability,
        }

        references = {
            'id': doc['id'],
            'answers': doc['answers'],
        }

        if self.save_examples:
            example = {
                "pred": pred,
                "target": doc['answers'],
            }
        return { 
            'exact': (predictions, references), # Exact match (the normalized answer exactly match the gold answer)
            'f1': (predictions, references), #  The F-score of predicted tokens versus the gold answer
            'HasAns_exact': (predictions, references), # Exact match (the normalized answer exactly match the gold answer)
            'HasAns_f1': (predictions, references), # The F-score of predicted tokens versus the gold answer
            'best_exact_thresh': (predictions, references), # Exact match (the normalized answer exactly match the gold answer)
            'best_f1_thresh': (predictions, references), # The F-score of predicted tokens versus the gold answer
            'best_exact': (predictions, references), # Best exact match (with varying threshold)
            'best_f1': (predictions, references), # Best F1 (with varying threshold)
        }, example

    def aggregation(self):
        """
        :returns: {str: [float] -> float}
            A dictionary where keys are the names of submetrics and values are 
            functions that aggregate a list of metrics
        """
        return { 
            'exact': partial(_squad_agg, 'exact'), # Exact match (the normalized answer exactly match the gold answer)
            'f1': partial(_squad_agg, 'f1'), #  The F-score of predicted tokens versus the gold answer
            'HasAns_exact': partial(_squad_agg, 'HasAns_exact'), # Exact match (the normalized answer exactly match the gold answer)
            'HasAns_f1': partial(_squad_agg, 'HasAns_f1'), # The F-score of predicted tokens versus the gold answer
            'best_exact_thresh': partial(_squad_agg, 'best_exact_thresh'), # Exact match (the normalized answer exactly match the gold answer)
            'best_f1_thresh': partial(_squad_agg, 'best_f1_thresh'), # The F-score of predicted tokens versus the gold answer
            'best_exact': partial(_squad_agg, 'best_exact'), # Best exact match (with varying threshold)
            'best_f1': partial(_squad_agg, 'best_f1'), # Best F1 (with varying threshold)
        }

    def higher_is_better(self):
        """
        :returns: {str: bool}
            A dictionary where keys are the names of submetrics and values are 
            whether a higher value of the submetric is better
        """
        return { 
            'exact': True, # Exact match (the normalized answer exactly match the gold answer)
            'f1': True, #  The F-score of predicted tokens versus the gold answer
            'HasAns_exact': True, # Exact match (the normalized answer exactly match the gold answer)
            'HasAns_f1': True, # The F-score of predicted tokens versus the gold answer
            'best_exact_thresh': True, # Exact match (the normalized answer exactly match the gold answer)
            'best_f1_thresh': True, # The F-score of predicted tokens versus the gold answer
            'best_exact': True, # Best exact match (with varying threshold)
            'best_f1': True, # Best F1 (with varying threshold)
        }
