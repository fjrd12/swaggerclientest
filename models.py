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

#***********************************************Tokenization********************************

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

sequence = "Using a Transformer network is simple"
tokens = tokenizer.tokenize(sequence)
print(tokens)
ids = tokenizer.convert_tokens_to_ids(tokens)
print(ids)
decoded_string = tokenizer.decode(ids)
print(decoded_string)

#******************************************Handling multiples sequences*********************
checkpoint = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(checkpoint)

sequence = "I've been waiting for a HuggingFace course my whole life."

tokens = tokenizer.tokenize(sequence)
ids = tokenizer.convert_tokens_to_ids(tokens)

input_ids = torch.tensor([ids])
print("Input IDs:", input_ids)

output = model(input_ids)
print("Logits:", output.logits)

batched_ids = [ids, ids]
print(batched_ids)

padding_id = 100

batched_ids2 = [
    [200, 200, 200],
    [200, 200, padding_id],
]

tensor = torch.tensor(batched_ids2)

sequence1_ids = [[200, 200, 200]]
sequence2_ids = [[200, 200]]
batched_ids = [
    [200, 200, 200],
    [200, 200, tokenizer.pad_token_id],
]

print(model(torch.tensor(sequence1_ids)).logits)
print(model(torch.tensor(sequence2_ids)).logits)
print(model(torch.tensor(batched_ids)).logits)