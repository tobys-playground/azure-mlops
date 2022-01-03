import numpy as np
from sklearn.model_selection import train_test_split
import ktrain
from ktrain import text
from azureml.core import Run
from sklearn.metrics import accuracy_score
from azureml.core import Dataset
from transformers.convert_graph_to_onnx import convert, optimize, quantize
from transformers import AutoModelForSequenceClassification
import onnxruntime, onnx
from pathlib import Path, PosixPath

#Get the experiment run context
run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace

#register dataset
print("Loading training data...")
default_ds = ws.get_default_datastore()
meld_dd_ds = Dataset.Tabular.from_delimited_files(path=(default_ds, 'meld-dd-sample.csv'))
meld_dd_ds = meld_dd_ds.register(workspace=ws, 
                                name='MELD-DD dataset',
                                description='MELD-DD data',
                                tags = {'format':'CSV'},
                                create_new_version=True)

df = meld_dd_ds.to_pandas_dataframe()

df = df[['Emotion','Statement']]

y = df.pop('Emotion')
X = df

X_train,X_test,y_train,y_test = train_test_split(X.to_numpy().ravel() ,y.to_numpy().ravel(),test_size=0.5)

#Hyperparameter values
learning_rate = 5e-5
epoch = 1

Emotions = ['joy', 'neutral']

#MODEL_NAME = 'distilbert-base-uncased'
MODEL_NAME = 'albert-base-v2'

t = text.Transformer(MODEL_NAME, maxlen=200, class_names=Emotions)
trn = t.preprocess_train(X_train, y_train)
val = t.preprocess_test(X_test, y_test)
model = t.get_classifier()
learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=24)

print("Learning_rate: " + str(learning_rate))
print("Epoch: " + str(epoch))

learner.fit_onecycle(learning_rate, epoch)
print("Results")

learner.validate(class_names=t.get_classes())

predictor = ktrain.get_predictor(learner.model, preproc=t) 

y_scores = predictor.predict_proba(X_test)
y_scores= np.argmax(y_scores, axis=1)
y_real= np.argmax(val.y, axis=1)

acc = accuracy_score(y_real, y_scores)
print('Accuracy: ' + str(acc))
run.log('Accuracy', np.float(acc))

ktrain_model_name = 'mgsa-ed'
#onnx_model_name = 'onnx_model_optimized_quantized'
onnx_model_name = 'model_optimized_quantized.onnx'

predictor.save(ktrain_model_name)
print('MODEL SAVED')

predictor_path = './' + ktrain_model_name
pt_path = predictor_path+'_pt'
pt_onnx_path = pt_path +'_onnx/model.onnx'

print(predictor_path)
print(pt_path)
print(pt_onnx_path)

AutoModelForSequenceClassification.from_pretrained(predictor_path, 
                                                   from_tf=True).save_pretrained(pt_path)
convert(framework='pt', model=pt_path,output=Path(pt_onnx_path), opset=13, 
        tokenizer=ktrain_model_name, pipeline_name='sentiment-analysis')
pt_onnx_quantized_path = quantize(optimize(Path(pt_onnx_path)))

print(pt_onnx_quantized_path)

# upload the model file explicitly into artifacts
#run.upload_folder(name="./outputs", path= './' + model_name)
run.upload_file(name='./outputs/' +  onnx_model_name, path_or_stream= './' + pt_onnx_quantized_path.as_posix())

print("Uploaded the model {} to experiment {}".format(onnx_model_name, run.experiment.name))

run.complete()