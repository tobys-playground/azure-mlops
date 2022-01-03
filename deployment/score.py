import json
import numpy as np
import time
import os
from transformers import AutoTokenizer

def create_onnx_session(onnx_model_path, provider='CPUExecutionProvider'):
    """
    Creates ONNX inference session from provided onnx_model_path
    """
    from onnxruntime import GraphOptimizationLevel, InferenceSession, SessionOptions, get_all_providers
    assert provider in get_all_providers(), f"provider {provider} not found, {get_all_providers()}"

    # Few properties that might have an impact on performances (provided by MS)
    options = SessionOptions()
    options.intra_op_num_threads = 0
    options.graph_optimization_level = GraphOptimizationLevel.ORT_ENABLE_ALL

    # Load the model as a graph and prepare the CPU backend 
    session = InferenceSession(onnx_model_path, options, providers=[provider])
    session.disable_fallback()
    return session

def init():
    global sess

    print ("session initialized" + time.strftime("%H:%M:%S"))
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'outputs', 'model_optimized_quantized.onnx')
    print(model_path)
    sess = create_onnx_session(model_path)

def run(raw_data):
    try:
        model_name = 'albert-base-v2'
        maxlen = 200
        class_names = ['joy', 'neutral']
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokens = tokenizer.encode_plus(str(raw_data), max_length=maxlen, truncation=True)
        tokens = {name: np.atleast_2d(value) for name, value in tokens.items()}
        print("predicted class: %s" % (class_names[np.argmax(sess.run(None, tokens)[0])]))
    except Exception as e:
        result = str(e)
        return result