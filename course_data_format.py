# 課程資料格式範例（course_data.json）
# 每筆課程記錄：title, description, schedule_slots, embedding

[
  {
    "title": "機器學習導論",
    "description": "本課程介紹監督式與非監督式學習、模型選擇與實作技巧。",
    "schedule_slots": ["1_3", "1_4", "3_3", "3_4"],
    "embedding": [0.01, 0.12, -0.04, ..., 0.033]  # 長度依你選定模型（如 OpenAI 1536 維）
  },
  {
    "title": "政治學概論",
    "description": "探討民主制度、政府體制與當代政治議題。",
    "schedule_slots": ["2_2", "2_3"],
    "embedding": [-0.005, 0.098, 0.032, ..., -0.072]
  }
  
  # ... 更多課程
]

# 🔸 schedule_slots：使用 weekday_index_節次 來表示（0~6 對應週一~週日）
# 🔸 embedding：為向量嵌入（待生成）
