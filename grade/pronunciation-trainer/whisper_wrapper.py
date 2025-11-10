import torch 
from transformers import pipeline
from ModelInterfaces import IASRModel
from typing import Union
import numpy as np 

class WhisperASRModel(IASRModel):
    def __init__(self, model_name="openai/whisper-base"):
        # 简化初始化，不使用 return_timestamps 参数
        self.asr = pipeline(
            "automatic-speech-recognition", 
            model=model_name
        )
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = 16000

    def processAudio(self, audio:Union[np.ndarray, torch.Tensor]):
        # 'audio' can be a path to a file or a numpy array of audio samples.
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        
        # 简单调用，不使用时间戳功能
        try:
            result = self.asr(audio[0])
        except Exception as e:
            print(f"Whisper处理失败: {e}")
            self._transcript = ""
            self._word_locations = []
            return
        
        # 获取转录文本
        self._transcript = result.get("text", "")
        
        # 由于不使用时间戳，估算词位置
        words = self._transcript.split()
        if words:
            avg_duration = len(audio[0]) / len(words)
            self._word_locations = [
                {
                    "word": word,
                    "start_ts": int(i * avg_duration),
                    "end_ts": int((i + 1) * avg_duration),
                    "tag": "estimated"
                }
                for i, word in enumerate(words)
            ]
        else:
            self._word_locations = []

    def getTranscript(self) -> str:
        return self._transcript

    def getWordLocations(self) -> list:
        return self._word_locations