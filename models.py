from transformers import AutoTokenizer, AutoModel,AutoModelForSequenceClassification
import torch
import numpy as np

checkpoint = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

raw_inputs = [
    "I've been waiting for a HuggingFace course my whole life.",
    "I hate this so much!",
]
inputs = tokenizer(raw_inputs, padding=True, truncation=True, return_tensors="pt")
print(inputs)

checkpoint = "distilbert-base-uncased-finetuned-sst-2-english"
model = AutoModel.from_pretrained(checkpoint)

outputs = model(**inputs)
print(outputs.last_hidden_state.shape)

checkpoint = "distilbert-base-uncased-finetuned-sst-2-english"
model = AutoModelForSequenceClassification.from_pretrained(checkpoint)
outputs = model(**inputs)
print(outputs.logits.shape)

predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

# Convert the tensor to a NumPy array
predictions_np = predictions.detach().numpy()

# Convert the tensor to a Python list
predictions_list = predictions.detach().tolist()

results = []

# Iterate over the dict model.config.id2label and zip with predictions_list
for i, prediction in enumerate(predictions_list):
    
    result_details = []
    for label_id, label in model.config.id2label.items():
        result_details.append((label, prediction[label_id]))
    results.append( (raw_inputs[i],result_details))

print(results)



