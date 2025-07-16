
import pandas as pd
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
from torch.optim import AdamW
from tqdm import tqdm # tqdm.notebook 대신 tqdm 임포트

# 1. 데이터 로드
df = pd.read_csv("/home/ubuntu/preprocessed_chatbot_data.csv")

# 2. 데이터셋 클래스 정의
class ChatbotDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = 128 # 최대 시퀀스 길이

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        q = self.data.iloc[idx]["Q_tokenized"]
        a = self.data.iloc[idx]["A_tokenized"]

        # 질문과 답변을 결합하여 모델 입력으로 사용
        # EOS 토큰을 사용하여 질문과 답변을 구분
        text = q + self.tokenizer.eos_token + a

        # 토큰화 및 인코딩
        inputs = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        return {
            "input_ids": inputs["input_ids"].flatten(),
            "attention_mask": inputs["attention_mask"].flatten()
        }

# 3. 모델 및 토크나이저 로드
tokenizer = PreTrainedTokenizerFast.from_pretrained("skt/kogpt2-base-v2",
    bos_token="<s>",
    eos_token="</s>",
    unk_token="<unk>",
    pad_token="<pad>",
    mask_token="<mask>"
)

model = GPT2LMHeadModel.from_pretrained("skt/kogpt2-base-v2")

# 4. 데이터셋 및 데이터로더 생성
train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)

train_dataset = ChatbotDataset(train_df, tokenizer)
val_dataset = ChatbotDataset(val_df, tokenizer)

train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=8)

# 5. 모델 학습 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.train()

optimizer = AdamW(model.parameters(), lr=5e-5)

epochs = 3 # 에폭 수

# 6. 모델 학습
for epoch in range(epochs):
    total_loss = 0
    for batch in tqdm(train_loader, desc=f"Epoch {epoch+1} Training"):
        optimizer.zero_grad()
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)

        outputs = model(input_ids, attention_mask=attention_mask, labels=input_ids)
        loss = outputs.loss
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1} Average Loss: {total_loss / len(train_loader):.4f}")

    # 검증
    model.eval()
    val_loss = 0
    with torch.no_grad():
        for batch in tqdm(val_loader, desc=f"Epoch {epoch+1} Validation"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            outputs = model(input_ids, attention_mask=attention_mask, labels=input_ids)
            loss = outputs.loss
            val_loss += loss.item()
    print(f"Epoch {epoch+1} Validation Loss: {val_loss / len(val_loader):.4f}")
    model.train()

# 7. 모델 저장
model.save_pretrained("/home/ubuntu/chatbot_model")
tokenizer.save_pretrained("/home/ubuntu/chatbot_model")
print("모델 학습 및 저장이 완료되었습니다: /home/ubuntu/chatbot_model")


