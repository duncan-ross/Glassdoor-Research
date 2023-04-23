import torch
import torch.nn as nn
from transformers import AutoModel
from torch.nn import functional as F
from typing import Any

class BaseModel(torch.nn.Module):
    def __init__(self, seq_length: int, num_outputs: int, pretrain_model_name: str):
        super(BaseModel, self).__init__()
        self.seq_length = seq_length
        self.l1 = AutoModel.from_pretrained(pretrain_model_name, trust_remote_code=True)
        self.l2 = torch.nn.Dropout(0.3)
        self.l3 = torch.nn.Linear(self.seq_length*768, self.seq_length)
        self.conv = torch.nn.Conv1d(in_channels=self.seq_length, out_channels=self.seq_length, kernel_size=3, padding="same")
        self.l4 = torch.nn.ReLU()
        self.l5 = torch.nn.Dropout(0.3)
        self.l6 = torch.nn.Linear(self.seq_length, num_outputs)

        
    def forward(self, data: Any, targets: Any = None, eval_output: bool = False, **kwargs):
        output_1= self.l1(input_ids=data['input_ids'].squeeze(1), attention_mask = data['attention_mask'].squeeze(1))
        output_2 = self.l2(output_1['last_hidden_state'].reshape(-1, self.seq_length*768))
        output_3 = self.conv(torch.permute(self.l3(output_2), (1, 0)))
        output_4 = self.l4(torch.permute(output_3, (1, 0)))
        output_5 = self.l5(output_4)
        output = self.l6(output_5)
        # if we are given some desired targets also calculate the loss
        loss = None
        if targets is not None:
            loss = nn.MSELoss()(output.float(), targets.float())
        return output, loss