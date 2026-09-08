import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import pandas as pd
from datetime import datetime




class ScheduleViewer:
   def __init__(self, root):
       self.root = root
       self.root.title("KBO 경기 일정 뷰어")
       self.root.geometry("1280x720")
       self.root.resizable(True, True)


       # --- 상단 프레임 ---
       top_frame = tk.Frame(root)
       top_frame.pack(fill='x', padx=10, pady=10)


       tk.Label(top_frame, text="월 선택:", font=("맑은 고딕", 12)).pack(side='left')


       self.month_combo = ttk.Combobox(top_frame, values=[f"{i:02d}" for i in range(1, 13)], state="readonly", width=5,
                                       font=("맑은 고딕", 11))
       self.month_combo.pack(side='left', padx=(5, 15))


       # 현재 월 자동 선택
       current_month = datetime.now().month
       self.month_combo.current(current_month - 1)


       # 이전/다음 월 버튼
       prev_btn = tk.Button(top_frame, text="<< 이전 월", font=("맑은 고딕", 11),
                            command=lambda: self.change_month(-1), bg="#FFC107", fg="black", relief='flat')
       prev_btn.pack(side='left', padx=5)


       next_btn = tk.Button(top_frame, text="다음 월 >>", font=("맑은 고딕", 11),
                            command=lambda: self.change_month(1), bg="#FFC107", fg="black", relief='flat')
       next_btn.pack(side='left', padx=5)


       # --- 필터 프레임 ---
       filter_frame = tk.LabelFrame(root, text="조건 필터", font=("맑은 고딕", 11))
       filter_frame.pack(fill='x', padx=10, pady=(0, 20))


       # 날짜 필터
       tk.Label(filter_frame, text="날짜:", font=("맑은 고딕", 11)).grid(row=0, column=0, padx=5, pady=5, sticky='e')
       self.date_var = tk.StringVar()
       self.date_entry = tk.Entry(filter_frame, textvariable=self.date_var, font=("맑은 고딕", 11), width=12)
       self.date_entry.grid(row=0, column=1, padx=5, pady=5)


       # 시간 필터
       tk.Label(filter_frame, text="시간:", font=("맑은 고딕", 11)).grid(row=0, column=2, padx=5, pady=5, sticky='e')
       self.time_var = tk.StringVar()
       self.time_entry = tk.Entry(filter_frame, textvariable=self.time_var, font=("맑은 고딕", 11), width=10)
       self.time_entry.grid(row=0, column=3, padx=5, pady=5)


       # 경기 상대 필터
       tk.Label(filter_frame, text="경기 상대:", font=("맑은 고딕", 11)).grid(row=0, column=4, padx=5, pady=5, sticky='e')
       self.opponent_var = tk.StringVar()
       self.opponent_entry = tk.Entry(filter_frame, textvariable=self.opponent_var, font=("맑은 고딕", 11), width=15)
       self.opponent_entry.grid(row=0, column=5, padx=5, pady=5)


       # 중계(구장) 필터
       tk.Label(filter_frame, text="중계(구장):", font=("맑은 고딕", 11)).grid(row=0, column=6, padx=5, pady=5, sticky='e')
       self.broadcast_var = tk.StringVar()
       self.broadcast_entry = tk.Entry(filter_frame, textvariable=self.broadcast_var, font=("맑은 고딕", 11), width=15)
       self.broadcast_entry.grid(row=0, column=7, padx=5, pady=5)


       # 우천 취소 체크박스
       self.rain_var = tk.BooleanVar()
       tk.Checkbutton(filter_frame, text="우천취소만 보기", variable=self.rain_var,
                      font=("맑은 고딕", 11)).grid(row=0, column=8, padx=10, pady=5, sticky='w')


       # 필터 적용 버튼
       self.btn_filter = tk.Button(filter_frame, text="필터 적용", font=("맑은 고딕", 11),
                                   command=self.apply_filters, bg="#2196F3", fg="white", relief='flat')
       self.btn_filter.grid(row=0, column=12, padx=10, pady=5)


       # Enter 키로 필터 적용 (root 전체에 바인딩)
       self.root.bind("<Return>", lambda event: self.apply_filters())


       # --- 테이블 프레임 ---
       table_frame = tk.Frame(root)
       table_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))


       self.tree = ttk.Treeview(table_frame, show='headings')
       self.tree.pack(side='left', fill='both', expand=True)


       scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
       scrollbar.pack(side='right', fill='y')
       self.tree.configure(yscroll=scrollbar.set)


       self.df = pd.DataFrame()


       # 프로그램 시작 시 현재 월 일정 자동 조회
       self.load_schedule()


   # 이전/다음 월 버튼 기능
   def change_month(self, offset):
       month = int(self.month_combo.get()) + offset
       if month < 1:
           month = 12
       elif month > 12:
           month = 1
       self.month_combo.set(f"{month:02d}")
       self.load_schedule()  # 월 변경 시 자동 조회


   # 일정 로드
   def load_schedule(self):
       month = self.month_combo.get()
       if not month:
           messagebox.showwarning("알림", "월을 선택해주세요.")
           return


       filepath = rf'C:\pca\{month}m_calender.json'
       if not os.path.exists(filepath):
           messagebox.showerror("오류", f"{month}월 경기 일정 파일이 없습니다.")
           self.df = pd.DataFrame()
           self.tree.delete(*self.tree.get_children())
           return


       with open(filepath, 'r', encoding='utf-8') as f:
           data = json.load(f)


       if isinstance(data, dict) and 'games' in data:
           data = data['games']


       if not data:
           messagebox.showinfo("정보", "해당 월에 경기 일정이 없습니다.")
           self.df = pd.DataFrame()
           self.tree.delete(*self.tree.get_children())
           return


       self.df = pd.DataFrame(data)
       self.tree.delete(*self.tree.get_children())
       self.tree["columns"] = list(self.df.columns)
       for col in self.df.columns:
           self.tree.heading(col, text=col, anchor='center')
           self.tree.column(col, anchor='center', width=110, minwidth=90)
       for _, row in self.df.iterrows():
           self.tree.insert("", "end", values=list(row))


   # 필터 적용
   def apply_filters(self):
       if self.df.empty:
           return


       df_filtered = self.df.copy()
       date_filter = self.date_var.get().strip().lower()
       time_filter = self.time_var.get().strip().lower()
       opponent_filter = self.opponent_var.get().strip().lower()
       stadium_filter = self.broadcast_var.get().strip().lower()
       rain_checked = self.rain_var.get()


       if date_filter and '날짜' in df_filtered.columns:
           df_filtered = df_filtered[df_filtered['날짜'].str.lower().str.contains(date_filter, na=False)]
       if time_filter and '시간' in df_filtered.columns:
           df_filtered = df_filtered[df_filtered['시간'].str.lower().str.contains(time_filter, na=False)]
       if opponent_filter and '경기' in df_filtered.columns:
           df_filtered = df_filtered[df_filtered['경기'].astype(str).str.lower().str.contains(opponent_filter, na=False)]
       if stadium_filter and '구장' in df_filtered.columns:
           df_filtered = df_filtered[df_filtered['구장'].astype(str).str.lower().str.contains(stadium_filter, na=False)]
       if rain_checked:
           if '비고' in df_filtered.columns and 'TV' in df_filtered.columns:
               df_filtered = df_filtered[
                   df_filtered['비고'].astype(str).str.contains('우천', na=False) |
                   df_filtered['TV'].astype(str).str.contains('우천', na=False)
               ]
           elif '비고' in df_filtered.columns:
               df_filtered = df_filtered[df_filtered['비고'].astype(str).str.contains('우천', na=False)]
           elif 'TV' in df_filtered.columns:
               df_filtered = df_filtered[df_filtered['TV'].astype(str).str.contains('우천', na=False)]


       self.tree.delete(*self.tree.get_children())
       for _, row in df_filtered.iterrows():
           self.tree.insert("", "end", values=list(row))




if __name__ == "__main__":
   root = tk.Tk()
   app = ScheduleViewer(root)
   root.mainloop()
