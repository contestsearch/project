import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import difflib
from PIL import Image, ImageTk
import webbrowser
import threading

class IdeaDuplicateChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("아이디어 중복 검사기 - 이거 이미 있어")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 색상 테마 설정
        self.bg_color = "#f0f0f0"
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#6b88b5"
        self.text_color = "#333333"
        self.highlight_color = "#ff6b6b"
        self.success_color = "#4caf50"
        
        self.root.configure(bg=self.bg_color)
        
        # 아이콘 및 스타일 설정
        self.style = ttk.Style()
        self.style.configure("TButton", 
                             font=("맑은 고딕", 10),
                             background=self.primary_color)
        self.style.configure("TLabel", 
                             font=("맑은 고딕", 11),
                             background=self.bg_color,
                             foreground=self.text_color)
        self.style.configure("Title.TLabel", 
                             font=("맑은 고딕", 16, "bold"),
                             background=self.bg_color,
                             foreground=self.primary_color)
        
        # 메인 프레임
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 타이틀
        self.title_label = ttk.Label(self.main_frame, 
                                     text="아이디어 중복 검사기 - 이거 이미 있어어", 
                                     style="Title.TLabel")
        self.title_label.pack(pady=(0, 20))
        
        # 설명 텍스트
        self.desc_text = "공모전 아이디어의 중복 여부를 확인하기 위해 아이디어 제목을 입력하세요.\nKIPRIS API를 통해 유사한 아이디어를 검색합니다."
        self.desc_label = ttk.Label(self.main_frame, text=self.desc_text, wraplength=700)
        self.desc_label.pack(pady=(0, 15))
        
        # 입력 프레임
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.idea_label = ttk.Label(self.input_frame, text="아이디어 제목:")
        self.idea_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.idea_entry = ttk.Entry(self.input_frame, width=50, font=("맑은 고딕", 11))
        self.idea_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.search_button = ttk.Button(self.input_frame, 
                                       text="검색", 
                                       command=self.search_idea)
        self.search_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 결과 표시 프레임
        self.result_frame = ttk.LabelFrame(self.main_frame, text="검색 결과", padding=10)
        self.result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 상태 표시 프레임
        self.status_frame = ttk.Frame(self.result_frame)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, 
                                     text="아이디어를 입력하고 검색 버튼을 클릭하세요.",
                                     font=("맑은 고딕", 10))
        self.status_label.pack(side=tk.LEFT)
        
        self.similarity_frame = ttk.Frame(self.status_frame)
        self.similarity_frame.pack(side=tk.RIGHT)
        
        self.similarity_label = ttk.Label(self.similarity_frame, 
                                        text="유사도: ",
                                        font=("맑은 고딕", 10))
        self.similarity_label.pack(side=tk.LEFT)
        
        self.similarity_value = ttk.Label(self.similarity_frame, 
                                        text="0%",
                                        font=("맑은 고딕", 10, "bold"))
        self.similarity_value.pack(side=tk.LEFT)
        
        # 결과 리스트 및 스크롤바
        self.result_list_frame = ttk.Frame(self.result_frame)
        self.result_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.result_list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.columns = ("순위", "아이디어명", "주최기관", "연도", "유사도")
        self.result_tree = ttk.Treeview(self.result_list_frame, 
                                       columns=self.columns,
                                       show="headings",
                                       selectmode="browse",
                                       height=10)
        
        # 헤더 설정
        self.result_tree.heading("순위", text="순위")
        self.result_tree.heading("아이디어명", text="아이디어명")
        self.result_tree.heading("주최기관", text="주최기관")
        self.result_tree.heading("연도", text="연도")
        self.result_tree.heading("유사도", text="유사도")
        
        # 컬럼 너비 설정
        self.result_tree.column("순위", width=50, anchor=tk.CENTER)
        self.result_tree.column("아이디어명", width=300, anchor=tk.W)
        self.result_tree.column("주최기관", width=150, anchor=tk.W)
        self.result_tree.column("연도", width=80, anchor=tk.CENTER)
        self.result_tree.column("유사도", width=80, anchor=tk.CENTER)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.result_tree.yview)
        self.result_tree.config(yscrollcommand=self.scrollbar.set)
        
        # 더블 클릭 이벤트 바인딩
        self.result_tree.bind("<Double-1>", self.show_details)
        
        # 상세 정보 프레임
        self.detail_frame = ttk.LabelFrame(self.main_frame, text="상세 정보", padding=10)
        self.detail_frame.pack(fill=tk.BOTH, pady=(15, 0))
        
        self.detail_text = scrolledtext.ScrolledText(self.detail_frame, 
                                                    width=40, 
                                                    height=5, 
                                                    wrap=tk.WORD,
                                                    font=("맑은 고딕", 10))
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # 버튼 프레임
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.link_button = ttk.Button(self.button_frame, 
                                     text="원문 링크 열기", 
                                     command=self.open_link,
                                     state=tk.DISABLED)
        self.link_button.pack(side=tk.RIGHT)
        
        # 데이터 저장용 변수
        self.search_results = []
        self.current_selected_link = ""
        
        # API 설정
        self.api_key = "SAMPLE_KIPRIS_API_KEY"  # 실제 API 키로 대체 필요
        self.api_url = "https://kipris.or.kr/api/competition"  # 예시 URL
        
        # 진행 상태 표시용 변수
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame, 
                                       orient=tk.HORIZONTAL, 
                                       length=100, 
                                       mode='determinate',
                                       variable=self.progress_var)
        
    def search_idea(self):
        """아이디어 검색 함수"""
        idea_name = self.idea_entry.get().strip()
        
        if not idea_name:
            messagebox.showwarning("입력 오류", "아이디어 제목을 입력해주세요.")
            return
        
        # 상태 업데이트
        self.status_label.config(text="검색 중...")
        self.progress.pack(fill=tk.X, pady=(10, 0))
        self.progress_var.set(0)
        
        # 기존 결과 삭제
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 스레드로 실행하여 UI 멈춤 방지
        thread = threading.Thread(target=self.search_idea_thread, args=(idea_name,))
        thread.daemon = True
        thread.start()
    
    def search_idea_thread(self, idea_name):
        """아이디어 검색 스레드 함수"""
        try:
            # 실제 API 호출 대신 샘플 데이터 생성
            # 실제 구현 시 API 호출 코드로 대체
            sample_data = self.get_sample_data(idea_name)
            
            # 진행 상태 표시
            for i in range(10):
                self.root.after(100, lambda v=i*10: self.progress_var.set(v))
                self.root.update_idletasks()
            
            # 검색 결과 처리
            self.search_results = []
            
            # 유사도 계산 및 정렬
            for idx, item in enumerate(sample_data):
                similarity = self.calculate_similarity(idea_name, item['title'])
                item['similarity'] = similarity
                self.search_results.append(item)
            
            # 유사도 순으로 정렬
            self.search_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # 결과 표시
            self.root.after(0, self.update_result_list)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("오류", f"검색 중 오류가 발생했습니다: {str(e)}"))
        finally:
            # 진행 상태 표시 제거
            self.root.after(0, lambda: self.progress.pack_forget())
    
    def update_result_list(self):
        """검색 결과 리스트 업데이트"""
        # 결과 표시
        for idx, item in enumerate(self.search_results):
            similarity_percent = f"{item['similarity']:.1f}%"
            self.result_tree.insert("", tk.END, 
                                    values=(idx+1, 
                                           item['title'], 
                                           item['organization'], 
                                           item['year'], 
                                           similarity_percent))
        
        # 상태 업데이트
        if self.search_results:
            max_similarity = self.search_results[0]['similarity']
            self.similarity_value.config(text=f"{max_similarity:.1f}%")
            
            if max_similarity > 80:
                self.status_label.config(text="※ 주의: 유사한 아이디어가 존재합니다!")
                self.similarity_value.config(foreground=self.highlight_color)
            elif max_similarity > 50:
                self.status_label.config(text="※ 참고: 부분적으로 유사한 아이디어가 있습니다.")
                self.similarity_value.config(foreground="orange")
            else:
                self.status_label.config(text="✓ 유사한 아이디어가 발견되지 않았습니다.")
                self.similarity_value.config(foreground=self.success_color)
        else:
            self.status_label.config(text="검색 결과가 없습니다.")
            self.similarity_value.config(text="0%")
    
    def calculate_similarity(self, text1, text2):
        """문자열 유사도 계산 함수"""
        # difflib의 SequenceMatcher를 사용한 유사도 계산
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio() * 100
        return similarity
    
    def get_sample_data(self, idea_name):
        """샘플 데이터 반환 (실제 API 호출 대체)"""
        # 실제 구현 시 API 호출 코드로 대체
        sample_data = [
            {
                "id": 1,
                "title": "효율적인 시간표 작성 도우미 앱",
                "organization": "대한민국 정보통신부",
                "year": "2023",
                "description": "대학생들의 시간표 작성을 돕는 앱으로, 강의 시간 충돌 확인과 여유 시간 최적화 기능을 제공합니다.",
                "link": "https://example.com/idea/1"
            },
            {
                "id": 2,
                "title": "AI 기반 효율적 시간표 생성 시스템",
                "organization": "한국소프트웨어산업협회",
                "year": "2022",
                "description": "인공지능을 활용하여 사용자의 선호도와 필수 과목을 고려한 최적의 시간표를 자동으로 생성해주는 시스템입니다.",
                "link": "https://example.com/idea/2"
            },
            {
                "id": 3,
                "title": "효율적 업무 시간 관리 솔루션",
                "organization": "중소벤처기업부",
                "year": "2023",
                "description": "기업 내 업무 효율성을 높이기 위한 시간 관리 솔루션으로, 업무 분배와 일정 조율 기능을 제공합니다.",
                "link": "https://example.com/idea/3"
            },
            {
                "id": 4,
                "title": "학교 시간표 자동화 시스템",
                "organization": "교육부",
                "year": "2021",
                "description": "초중고등학교의 시간표 작성을 자동화하여 교사의 업무 부담을 줄이고 효율적인 교육과정 운영을 돕는 시스템입니다.",
                "link": "https://example.com/idea/4"
            },
            {
                "id": 5,
                "title": "대중교통 효율적 이용 앱",
                "organization": "국토교통부",
                "year": "2022",
                "description": "대중교통 이용 시 최적 경로와 시간을 계산해주는 앱으로, 환승 시간과 대기 시간을 최소화합니다.",
                "link": "https://example.com/idea/5"
            },
            {
                "id": 6,
                "title": "시간 절약형 레시피 공유 플랫폼",
                "organization": "농림축산식품부",
                "year": "2023",
                "description": "바쁜 현대인을 위한 시간 절약형 요리 레시피를 공유하는 플랫폼입니다.",
                "link": "https://example.com/idea/6"
            },
            {
                "id": 7,
                "title": "대학생 커리큘럼 최적화 도구",
                "organization": "한국대학교육협의회",
                "year": "2022",
                "description": "대학생들의 학기별 수강 과목을 최적화하여 졸업 요건을 효율적으로 충족할 수 있도록 돕는 도구입니다.",
                "link": "https://example.com/idea/7"
            },
            {
                "id": 8,
                "title": "효시짜: 효율적 시간표 작성 도우미",
                "organization": "SK텔레콤",
                "year": "2023",
                "description": "대학생들의 시간표 작성 효율성을 높이기 위한 웹 서비스로, 강의 시간 충돌 방지와 공강 시간 최적화 기능을 제공합니다.",
                "link": "https://example.com/idea/8"
            }
        ]
        return sample_data
    
    def show_details(self, event):
        """아이템 더블 클릭 시 상세 정보 표시"""
        selected_item = self.result_tree.selection()
        if not selected_item:
            return
        
        # 선택된 항목의 인덱스 가져오기
        idx = int(self.result_tree.item(selected_item[0], "values")[0]) - 1
        
        if 0 <= idx < len(self.search_results):
            item = self.search_results[idx]
            
            # 상세 정보 표시
            detail_info = f"아이디어명: {item['title']}\n"
            detail_info += f"주최기관: {item['organization']}\n"
            detail_info += f"연도: {item['year']}\n"
            detail_info += f"유사도: {item['similarity']:.1f}%\n\n"
            detail_info += f"상세내용: {item['description']}"
            
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, detail_info)
            
            # 링크 버튼 활성화
            self.link_button.config(state=tk.NORMAL)
            self.current_selected_link = item['link']
    
    def open_link(self):
        """원문 링크 열기"""
        if self.current_selected_link:
            webbrowser.open(self.current_selected_link)

def main():
    root = tk.Tk()
    app = IdeaDuplicateChecker(root)
    root.mainloop()

if __name__ == "__main__":
    main()