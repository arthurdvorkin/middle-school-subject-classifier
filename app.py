import streamlit as st
import torch
from peft import LoraConfig, PeftConfig, PeftModel, get_peft_model
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

from subjects import id2label, label2id

model_checkpoint = "distilbert/distilbert-base-uncased"
model = AutoModelForSequenceClassification.from_pretrained(
    model_checkpoint, num_labels=8, id2label=id2label, label2id=label2id
)
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint, add_prefix_space=True)
model = PeftModel.from_pretrained(model, "./saved-model1/")
model = model.merge_and_unload()


st.title("Middle School Subject Classifier")
with st.form(key="classifier"):
    text = st.text_area("Enter a text")
    submit_text = st.form_submit_button(label="Submit")
    if submit_text:
        inputs = tokenizer.encode(text, return_tensors="pt").to("cpu")
        logits = model(inputs).logits
        predictions = torch.max(logits, 1).indices
        st.text(
            f"Your text is middle school {id2label[predictions.tolist()[0]].lower()}"
        )
