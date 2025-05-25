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
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # 프리미엄 색상 테마 설정 (Dark Modern Theme)
        self.bg_color = "#1a1a1a"
        self.card_bg = "#2d2d2d"
        self.primary_color = "#6c5ce7"
        self.secondary_color = "#a29bfe"
        self.accent_color = "#fd79a8"
        self.success_color = "#00b894"
        self.warning_color = "#fdcb6e"
        self.danger_color = "#e84393"
        self.text_primary = "#ffffff"
        self.text_secondary = "#b2b2b2"
        self.border_color = "#404040"
        self.hover_color = "#404040"
        
        self.root.configure(bg=self.bg_color)
        
        # 커스텀 스타일 설정
        self.setup_custom_styles()
        
        # 메인 컨테이너 (패딩과 그림자 효과)
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 헤더 섹션
        self.create_header()
        
        # 검색 섹션
        self.create_search_section()
        
        # 결과 섹션
        self.create_results_section()
        
        # 상세 정보 섹션
        self.create_detail_section()
        
        # 데이터 저장용 변수
        self.search_results = []
        self.current_selected_link = ""
        
        # API 설정
        self.api_key = "SAMPLE_KIPRIS_API_KEY"
        self.api_url = "https://kipris.or.kr/api/competition"
        
        # 애니메이션 효과를 위한 변수
        self.animation_step = 0
        
    def setup_custom_styles(self):
        """커스텀 스타일 설정"""
        self.style = ttk.Style()
        
        # 버튼 스타일
        self.style.configure("Primary.TButton",
                           font=("Segoe UI", 11, "bold"),
                           foreground=self.text_primary,
                           background=self.primary_color,
                           borderwidth=0,
                           focuscolor="none",
                           relief="flat")
        
        self.style.map("Primary.TButton",
                      background=[("active", self.secondary_color),
                                ("pressed", self.primary_color)])
        
        self.style.configure("Secondary.TButton",
                           font=("Segoe UI", 10),
                           foreground=self.text_primary,
                           background=self.card_bg,
                           borderwidth=1,
                           relief="solid")
        
        # 라벨 스타일
        self.style.configure("Title.TLabel",
                           font=("Segoe UI", 28, "bold"),
                           foreground=self.primary_color,
                           background=self.bg_color)
        
        self.style.configure("Subtitle.TLabel",
                           font=("Segoe UI", 12),
                           foreground=self.text_secondary,
                           background=self.bg_color)
        
        self.style.configure("Header.TLabel",
                           font=("Segoe UI", 14, "bold"),
                           foreground=self.text_primary,
                           background=self.card_bg)
        
        self.style.configure("Body.TLabel",
                           font=("Segoe UI", 11),
                           foreground=self.text_primary,
                           background=self.card_bg)
        
        # 프레임 스타일
        self.style.configure("Card.TFrame",
                           background=self.card_bg,
                           relief="flat",
                           borderwidth=1)
        
        # 엔트리 스타일
        self.style.configure("Custom.TEntry",
                           font=("Segoe UI", 12),
                           foreground=self.text_primary,
                           fieldbackground=self.card_bg,
                           borderwidth=2,
                           insertcolor=self.primary_color)
        
        # 트리뷰 스타일
        self.style.configure("Custom.Treeview",
                           font=("Segoe UI", 10),
                           background=self.card_bg,
                           foreground=self.text_primary,
                           fieldbackground=self.card_bg,
                           borderwidth=0,
                           rowheight=35)
        
        self.style.configure("Custom.Treeview.Heading",
                           font=("Segoe UI", 11, "bold"),
                           foreground=self.text_primary,
                           background=self.primary_color,
                           borderwidth=0)
        
        self.style.map("Custom.Treeview",
                      background=[("selected", self.primary_color)])
    
    def create_header(self):
        """헤더 섹션 생성"""
        header_frame = tk.Frame(self.main_container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # 그라데이션 효과를 위한 캔버스
        header_canvas = tk.Canvas(header_frame, height=120, bg=self.bg_color, highlightthickness=0)
        header_canvas.pack(fill=tk.X)
        
        # 백그라운드 그라데이션 효과 (간단한 버전)
        for i in range(120):
            color_intensity = int(45 + (i * 0.2))  # 그라데이션 효과
            color = f"#{color_intensity:02x}{color_intensity:02x}{color_intensity:02x}"
            header_canvas.create_line(0, i, 1200, i, fill=color)
        
        # 메인 타이틀
        title_label = tk.Label(header_canvas, 
                              text="아이디어 중복 검사기",
                              font=("Segoe UI", 28, "bold"),
                              fg=self.text_primary,
                              bg=self.card_bg)
        header_canvas.create_window(600, 35, window=title_label)
        
        # 서브타이틀
        subtitle_label = tk.Label(header_canvas,
                                 text="💡 이거 이미 있어? - AI 기반 아이디어 중복성 분석 도구",
                                 font=("Segoe UI", 14),
                                 fg=self.accent_color,
                                 bg=self.card_bg)
        header_canvas.create_window(600, 70, window=subtitle_label)
        
        # 장식용 라인
        header_canvas.create_line(200, 95, 1000, 95, fill=self.primary_color, width=2)
    
    def create_search_section(self):
        """검색 섹션 생성"""
        search_container = tk.Frame(self.main_container, bg=self.bg_color)
        search_container.pack(fill=tk.X, pady=(0, 20))
        
        # 검색 카드
        search_card = tk.Frame(search_container, bg=self.card_bg, relief="raised", bd=1)
        search_card.pack(fill=tk.X, padx=10, pady=10)
        
        # 내부 패딩
        search_inner = tk.Frame(search_card, bg=self.card_bg)
        search_inner.pack(fill=tk.X, padx=30, pady=25)
        
        # 설명 텍스트
        desc_text = "🔍 공모전 아이디어의 중복 여부를 확인하세요. KIPRIS API를 통해 기존 아이디어와의 유사도를 분석합니다."
        desc_label = tk.Label(search_inner, 
                             text=desc_text,
                             font=("Segoe UI", 12),
                             fg=self.text_secondary,
                             bg=self.card_bg,
                             wraplength=800)
        desc_label.pack(pady=(0, 20))
        
        # 입력 프레임
        input_frame = tk.Frame(search_inner, bg=self.card_bg)
        input_frame.pack(fill=tk.X)
        
        # 입력 라벨
        input_label = tk.Label(input_frame,
                              text="아이디어 제목",
                              font=("Segoe UI", 12, "bold"),
                              fg=self.text_primary,
                              bg=self.card_bg)
        input_label.pack(anchor=tk.W, pady=(0, 8))
        
        # 입력 필드와 버튼을 담는 프레임
        entry_frame = tk.Frame(input_frame, bg=self.card_bg)
        entry_frame.pack(fill=tk.X)
        
        # 입력 필드
        self.idea_entry = tk.Entry(entry_frame,
                                  font=("Segoe UI", 14),
                                  bg=self.card_bg,
                                  fg=self.text_primary,
                                  insertbackground=self.primary_color,
                                  relief="solid",
                                  bd=2,
                                  highlightcolor=self.primary_color,
                                  highlightthickness=1)
        self.idea_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)
        
        # 검색 버튼
        self.search_button = tk.Button(entry_frame,
                                      text="🔍 검색하기",
                                      font=("Segoe UI", 12, "bold"),
                                      fg=self.text_primary,
                                      bg=self.primary_color,
                                      activebackground=self.secondary_color,
                                      activeforeground=self.text_primary,
                                      relief="flat",
                                      bd=0,
                                      padx=30,
                                      command=self.search_idea,
                                      cursor="hand2")
        self.search_button.pack(side=tk.RIGHT, padx=(15, 0), ipady=10)
        
        # 프로그레스바
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(search_inner,
                                       orient=tk.HORIZONTAL,
                                       length=100,
                                       mode='determinate',
                                       variable=self.progress_var,
                                       style="Custom.Horizontal.TProgressbar")
        
        # 프로그레스바 스타일
        self.style.configure("Custom.Horizontal.TProgressbar",
                           background=self.primary_color,
                           troughcolor=self.border_color,
                           borderwidth=0,
                           lightcolor=self.primary_color,
                           darkcolor=self.primary_color)
    
    def create_results_section(self):
        """결과 섹션 생성"""
        results_container = tk.Frame(self.main_container, bg=self.bg_color)
        results_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 결과 카드
        results_card = tk.Frame(results_container, bg=self.card_bg, relief="raised", bd=1)
        results_card.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # 결과 헤더
        results_header = tk.Frame(results_card, bg=self.card_bg)
        results_header.pack(fill=tk.X, padx=25, pady=(20, 0))
        
        header_left = tk.Frame(results_header, bg=self.card_bg)
        header_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        results_title = tk.Label(header_left,
                                text="📊 검색 결과",
                                font=("Segoe UI", 18, "bold"),
                                fg=self.text_primary,
                                bg=self.card_bg)
        results_title.pack(anchor=tk.W)
        
        # 상태 정보
        status_frame = tk.Frame(results_header, bg=self.card_bg)
        status_frame.pack(side=tk.RIGHT)
        
        self.status_label = tk.Label(status_frame,
                                    text="아이디어를 입력하고 검색 버튼을 클릭하세요.",
                                    font=("Segoe UI", 11),
                                    fg=self.text_secondary,
                                    bg=self.card_bg)
        self.status_label.pack(side=tk.TOP, anchor=tk.E)
        
        similarity_info = tk.Frame(status_frame, bg=self.card_bg)
        similarity_info.pack(side=tk.TOP, anchor=tk.E, pady=(5, 0))
        
        similarity_label = tk.Label(similarity_info,
                                   text="최고 유사도: ",
                                   font=("Segoe UI", 11),
                                   fg=self.text_secondary,
                                   bg=self.card_bg)
        similarity_label.pack(side=tk.LEFT)
        
        self.similarity_value = tk.Label(similarity_info,
                                        text="0%",
                                        font=("Segoe UI", 14, "bold"),
                                        fg=self.primary_color,
                                        bg=self.card_bg)
        self.similarity_value.pack(side=tk.LEFT)
        
        # 구분선
        separator = tk.Frame(results_card, height=2, bg=self.border_color)
        separator.pack(fill=tk.X, padx=25, pady=15)
        
        # 결과 리스트 프레임
        list_frame = tk.Frame(results_card, bg=self.card_bg)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))
        
        # 스크롤바와 트리뷰
        list_container = tk.Frame(list_frame, bg=self.card_bg)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar = ttk.Scrollbar(list_container, style="Custom.Vertical.TScrollbar")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 스크롤바 스타일
        self.style.configure("Custom.Vertical.TScrollbar",
                           background=self.card_bg,
                           troughcolor=self.border_color,
                           borderwidth=0,
                           arrowcolor=self.text_primary,
                           darkcolor=self.primary_color,
                           lightcolor=self.primary_color)
        
        self.columns = ("순위", "아이디어명", "주최기관", "연도", "유사도")
        self.result_tree = ttk.Treeview(list_container,
                                       columns=self.columns,
                                       show="headings",
                                       selectmode="browse",
                                       height=12,
                                       style="Custom.Treeview")
        
        # 헤더 설정
        self.result_tree.heading("순위", text="순위")
        self.result_tree.heading("아이디어명", text="아이디어명")
        self.result_tree.heading("주최기관", text="주최기관")
        self.result_tree.heading("연도", text="연도")
        self.result_tree.heading("유사도", text="유사도 (%)")
        
        # 컬럼 너비 설정
        self.result_tree.column("순위", width=60, anchor=tk.CENTER)
        self.result_tree.column("아이디어명", width=400, anchor=tk.W)
        self.result_tree.column("주최기관", width=200, anchor=tk.W)
        self.result_tree.column("연도", width=100, anchor=tk.CENTER)
        self.result_tree.column("유사도", width=100, anchor=tk.CENTER)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.result_tree.yview)
        self.result_tree.config(yscrollcommand=self.scrollbar.set)
        
        # 더블 클릭 이벤트 바인딩
        self.result_tree.bind("<Double-1>", self.show_details)
        self.result_tree.bind("<Button-1>", self.on_tree_select)
    
    def create_detail_section(self):
        """상세 정보 섹션 생성"""
        detail_container = tk.Frame(self.main_container, bg=self.bg_color)
        detail_container.pack(fill=tk.X)
        
        # 상세 정보 카드
        detail_card = tk.Frame(detail_container, bg=self.card_bg, relief="raised", bd=1)
        detail_card.pack(fill=tk.X, padx=10, pady=10)
        
        # 헤더
        detail_header = tk.Frame(detail_card, bg=self.card_bg)
        detail_header.pack(fill=tk.X, padx=25, pady=(20, 10))
        
        detail_title = tk.Label(detail_header,
                               text="📋 상세 정보",
                               font=("Segoe UI", 16, "bold"),
                               fg=self.text_primary,
                               bg=self.card_bg)
        detail_title.pack(side=tk.LEFT)
        
        # 링크 버튼
        self.link_button = tk.Button(detail_header,
                                    text="🔗 원문 보기",
                                    font=("Segoe UI", 10, "bold"),
                                    fg=self.text_primary,
                                    bg=self.accent_color,
                                    activebackground=self.danger_color,
                                    activeforeground=self.text_primary,
                                    relief="flat",
                                    bd=0,
                                    padx=20,
                                    pady=5,
                                    state=tk.DISABLED,
                                    command=self.open_link,
                                    cursor="hand2")
        self.link_button.pack(side=tk.RIGHT)
        
        # 구분선
        detail_separator = tk.Frame(detail_card, height=1, bg=self.border_color)
        detail_separator.pack(fill=tk.X, padx=25, pady=(10, 15))
        
        # 상세 텍스트
        detail_text_frame = tk.Frame(detail_card, bg=self.card_bg)
        detail_text_frame.pack(fill=tk.X, padx=25, pady=(0, 20))
        
        self.detail_text = tk.Text(detail_text_frame,
                                  width=40,
                                  height=6,
                                  wrap=tk.WORD,
                                  font=("Segoe UI", 11),
                                  bg=self.card_bg,
                                  fg=self.text_primary,
                                  insertbackground=self.primary_color,
                                  relief="flat",
                                  bd=0,
                                  selectbackground=self.primary_color,
                                  selectforeground=self.text_primary)
        
        detail_scrollbar = ttk.Scrollbar(detail_text_frame, orient="vertical", command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 플레이스홀더 텍스트
        placeholder_text = "항목을 선택하면 상세 정보가 여기에 표시됩니다.\n더블클릭하여 상세 정보를 확인하세요."
        self.detail_text.insert(tk.END, placeholder_text)
        self.detail_text.config(state=tk.DISABLED)
    
    def on_tree_select(self, event):
        """트리뷰 선택 시 시각적 피드백"""
        selection = self.result_tree.selection()
        if selection:
            # 선택된 항목에 대한 시각적 효과 (간단한 애니메이션)
            self.animate_selection()
    
    def animate_selection(self):
        """선택 애니메이션 효과"""
        # 간단한 색상 변화 애니메이션
        pass
    
    def search_idea(self):
        """아이디어 검색 함수"""
        idea_name = self.idea_entry.get().strip()
        
        if not idea_name:
            messagebox.showwarning("입력 오류", "아이디어 제목을 입력해주세요.")
            return
        
        # 검색 버튼 비활성화
        self.search_button.config(state=tk.DISABLED, text="🔄 검색 중...")
        
        # 상태 업데이트
        self.status_label.config(text="🔍 검색 중... 잠시만 기다려주세요.")
        self.progress.pack(fill=tk.X, pady=(15, 0))
        self.progress_var.set(0)
        
        # 기존 결과 삭제
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 상세 정보 초기화
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, "검색 중입니다...")
        self.detail_text.config(state=tk.DISABLED)
        
        # 스레드로 실행하여 UI 멈춤 방지
        thread = threading.Thread(target=self.search_idea_thread, args=(idea_name,))
        thread.daemon = True
        thread.start()
    
    def search_idea_thread(self, idea_name):
        """아이디어 검색 스레드 함수"""
        try:
            # 실제 API 호출 대신 샘플 데이터 생성
            sample_data = self.get_sample_data(idea_name)
            
            # 진행 상태 표시
            for i in range(10):
                self.root.after(0, lambda v=i*10: self.progress_var.set(v))
                threading.Event().wait(0.1)
            
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
            # 진행 상태 표시 제거 및 버튼 복원
            self.root.after(0, self.search_complete)
    
    def search_complete(self):
        """검색 완료 처리"""
        self.progress.pack_forget()
        self.search_button.config(state=tk.NORMAL, text="🔍 검색하기")
    
    def update_result_list(self):
        """검색 결과 리스트 업데이트"""
        # 결과 표시
        for idx, item in enumerate(self.search_results):
            similarity_percent = f"{item['similarity']:.1f}"
            
            # 유사도에 따른 색상 태그 설정
            if item['similarity'] > 80:
                tag = "high_similarity"
            elif item['similarity'] > 50:
                tag = "medium_similarity"
            else:
                tag = "low_similarity"
            
            self.result_tree.insert("", tk.END,
                                    values=(idx+1,
                                           item['title'],
                                           item['organization'],
                                           item['year'],
                                           similarity_percent),
                                    tags=(tag,))
        
        # 태그 색상 설정
        self.result_tree.tag_configure("high_similarity", background="#ff6b6b", foreground="white")
        self.result_tree.tag_configure("medium_similarity", background="#fdcb6e", foreground="black")
        self.result_tree.tag_configure("low_similarity", background=self.card_bg, foreground=self.text_primary)
        
        # 상태 업데이트
        if self.search_results:
            max_similarity = self.search_results[0]['similarity']
            self.similarity_value.config(text=f"{max_similarity:.1f}%")
            
            if max_similarity > 80:
                self.status_label.config(text="⚠️ 주의: 매우 유사한 아이디어가 존재합니다!", fg=self.danger_color)
                self.similarity_value.config(fg=self.danger_color)
            elif max_similarity > 50:
                self.status_label.config(text="⚡ 참고: 부분적으로 유사한 아이디어가 있습니다.", fg=self.warning_color)
                self.similarity_value.config(fg=self.warning_color)
            else:
                self.status_label.config(text="✅ 유사한 아이디어가 발견되지 않았습니다.", fg=self.success_color)
                self.similarity_value.config(fg=self.success_color)
        else:
            self.status_label.config(text="❌ 검색 결과가 없습니다.", fg=self.text_secondary)
            self.similarity_value.config(text="0%", fg=self.text_secondary)
        
        # 상세 정보 초기화
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        if self.search_results:
            self.detail_text.insert(tk.END, "💡 항목을 더블클릭하여 상세 정보를 확인하세요.")
        else:
            self.detail_text.insert(tk.END, "검색 결과가 없습니다.")
        self.detail_text.config(state=tk.DISABLED)
    
    def calculate_similarity(self, text1, text2):
        """문자열 유사도 계산 함수"""
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio() * 100
        return similarity
    
    def get_sample_data(self, idea_name):
        """샘플 데이터 반환 (실제 API 호출 대체)"""
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
            
            # 상세 정보 표시 (더 예쁜 포맷)
            detail_info = f"🎯 아이디어명\n{item['title']}\n\n"
            detail_info += f"🏢 주최기관\n{item['organization']}\n\n"
            detail_info += f"📅 연도\n{item['year']}\n\n"
            detail_info += f"📊 유사도\n{item['similarity']:.1f}%\n\n"
            detail_info += f"📝 상세내용\n{item['description']}"
            
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, detail_info)
            self.detail_text.config(state=tk.DISABLED)
            
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