"""
Tool để hỏi thêm thông tin cho câu hỏi recruitment incomplete.
Chỉ hỏi thêm 1-2 thông tin quan trọng nhất để không làm phiền người dùng.
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum

class InfoType(Enum):
    """Các loại thông tin cần thu thập."""
    JOB_POSITION = "job_position"  # Vị trí công việc
    LOCATION = "location"          # Địa điểm
    EXPERIENCE = "experience"      # Kinh nghiệm
    SALARY = "salary"             # Lương
    WORK_TYPE = "work_type"       # Hình thức làm việc

class QuestionEnhancer:
    """Tool để hỏi thêm thông tin cho câu hỏi recruitment incomplete."""
    
    def __init__(self):
        # Từ khóa để nhận diện thông tin đã có trong câu hỏi
        self.job_keywords = {
    'lập trình': [
        'lập trình', 'developer', 'dev', 'programmer', 'coder',
        'engineer', 'kỹ sư phần mềm', 'software', 'backend', 'front end',
        'frontend', 'fullstack', 'mobile', 'android', 'ios', 'web'
    ],
    'marketing': [
        'marketing', 'sale', 'sales', 'bán hàng', 'kinh doanh',
        'digital marketing', 'seo', 'sem', 'quảng cáo', 'ads',
        'content', 'pr', 'truyền thông', 'market'
    ],
    'kế toán': [
        'kế toán', 'accounting', 'accountant', 'finance',
        'tài chính', 'thuế', 'tax', 'kiểm toán', 'auditor'
    ],
    'thiết kế': [
        'thiết kế', 'design', 'designer', 'đồ họa',
        'graphic', 'ui', 'ux', 'ui/ux', 'product design',
        'visual', 'illustrator', 'photoshop', 'figma'
    ],
    'data': [
        'data', 'analyst', 'analysis', 'scientist', 'science',
        'phân tích', 'dữ liệu', 'machine learning', 'ml', 'ai',
        'big data', 'data engineer', 'data architect'
    ],
    'qa': [
        'qa', 'test', 'tester', 'quality', 'quality assurance',
        'kiểm thử', 'manual test', 'automation test',
        'qa qc', 'qc', 'kiểm tra'
    ],
    'hr': [
        'hr', 'nhân sự', 'human resource', 'tuyển dụng',
        'recruitment', 'hành chính nhân sự', 'c&b',
        'chăm sóc nhân viên', 'people operation'
    ],
    'phục vụ': [
        'phục vụ', 'service', 'nhà hàng', 'quán', 'waiter', 'waitress',
        'barista', 'pha chế', 'bồi bàn', 'phục vụ bàn', 'lễ tân'
    ],
    'giáo dục': [
        'giáo viên', 'dạy học', 'teacher', 'education',
        'trợ giảng', 'gia sư', 'giảng viên', 'lecturer',
        'tutor', 'training', 'coach'
    ],
    'kỹ thuật': [
        'kỹ thuật', 'technician', 'maintenance',
        'bảo trì', 'cơ khí', 'điện', 'điện tử', 'electronics',
        'công nhân kỹ thuật'
    ]
}

        
        self.location_keywords = {
    'hà nội': ['hà nội', 'hn', 'hanoi'],
    'tp.hcm': ['tp.hcm', 'hcm', 'sài gòn', 'saigon', 'ho chi minh', 'hochiminh'],
    'đà nẵng': ['đà nẵng', 'da nang', 'danang'],
    'hải phòng': ['hải phòng', 'hai phong', 'hp'],
    'cần thơ': ['cần thơ', 'can tho'],
    'bình dương': ['bình dương', 'binh duong'],
    'đồng nai': ['đồng nai', 'dong nai'],
    'nha trang': ['nha trang', 'khanh hoa'],
    'quảng ninh': ['quảng ninh', 'quang ninh'],
    'huế': ['huế', 'hue', 'thừa thiên huế'],
    'remote': ['remote', 'từ xa', 'online', 'ở nhà', 'làm tại nhà', 'work from home', 'wfh']
}

        
        self.experience_keywords = [
    'kinh nghiệm', 'exp', 'experienced', 'chưa có kinh nghiệm', 'mới ra trường',
    'fresh', 'fresher', 'entry level', 'junior', 'middle', 'senior', 'lead',
    'intern', 'thực tập', 'trên', 'dưới', 'ít nhất', 'năm kinh nghiệm'
]

        self.salary_keywords = [
    'lương', 'salary', 'mức lương', 'thu nhập', 'trả', 'offer',
    'bao nhiêu', 'triệu', 'ngàn', 'usd', 'vnd', 'gross', 'net',
    'mức đãi ngộ', 'range', 'khoảng', 'tối thiểu', 'tối đa'
]

        self.work_type_keywords = [
    'full-time', 'full time', 'toàn thời gian',
    'part-time', 'part time', 'bán thời gian',
    'ca', 'ca sáng', 'ca tối', 'shift',
    'intern', 'thực tập', 'hợp đồng', 'contract',
    'remote', 'onsite', 'hybrid', 'tại văn phòng', 'làm từ xa'
]

        
        # Câu hỏi mẫu để thu thập thông tin
        self.question_templates = {
            InfoType.JOB_POSITION: [
                "Bạn muốn tìm việc ở vị trí nào? Ví dụ như lập trình viên, nhân viên marketing, kế toán...",
                "Bạn quan tâm đến công việc gì cụ thể?",
                "Lĩnh vực nào bạn muốn làm việc?"
            ],
            InfoType.LOCATION: [
                "Bạn muốn làm việc ở thành phố nào? (Hà Nội, TP.HCM, Đà Nẵng...) :D",
                "Địa điểm làm việc bạn ưu tiên là đâu?",
                "Bạn có thể làm việc tại khu vực nào?"
            ],
            InfoType.EXPERIENCE: [
                "Bạn có bao nhiều năm kinh nghiệm?",
                "Bạn là fresher hay đã có kinh nghiệm?",
                "Trình độ hiện tại của bạn như thế nào?"
            ],
            InfoType.SALARY: [
                "Mức lương bạn mong muốn khoảng bao nhiêu?",
                "Bạn kỳ vọng lương bao nhiêu?",
                "Khoảng thu nhập bạn quan tâm?"
            ],
            InfoType.WORK_TYPE: [
                "Bạn muốn làm full-time hay part-time?",
                "Hình thức làm việc bạn ưu tiên?",
                "Bạn có thể làm việc từ xa không?"
            ]
        }

    def analyze_incomplete_question(self, question: str) -> Dict[InfoType, bool]:
        """
        Phân tích câu hỏi incomplete để xác định thông tin nào đã có, thông tin nào thiếu.
        
        Args:
            question: Câu hỏi của người dùng
            
        Returns:
            Dict[InfoType, bool]: True nếu thông tin đã có, False nếu thiếu
        """
        question_lower = question.lower()
        info_status = {}
        
        # Kiểm tra vị trí công việc
        has_job_position = any(
            any(keyword in question_lower for keyword in keywords)
            for keywords in self.job_keywords.values()
        )
        info_status[InfoType.JOB_POSITION] = has_job_position
        
        # Kiểm tra địa điểm
        has_location = any(
            any(keyword in question_lower for keyword in keywords)
            for keywords in self.location_keywords.values()
        )
        info_status[InfoType.LOCATION] = has_location
        
        # Kiểm tra kinh nghiệm
        has_experience = any(keyword in question_lower for keyword in self.experience_keywords)
        info_status[InfoType.EXPERIENCE] = has_experience
        
        # Kiểm tra lương
        has_salary = any(keyword in question_lower for keyword in self.salary_keywords)
        info_status[InfoType.SALARY] = has_salary
        
        # Kiểm tra hình thức làm việc
        has_work_type = any(keyword in question_lower for keyword in self.work_type_keywords)
        info_status[InfoType.WORK_TYPE] = has_work_type
        
        return info_status

    def get_priority_missing_info(self, info_status: Dict[InfoType, bool]) -> List[InfoType]:
        """
        Xác định thứ tự ưu tiên của thông tin thiếu (chỉ lấy tối đa 2 thông tin quan trọng nhất).
        
        Thứ tự ưu tiên:
        1. Vị trí công việc (quan trọng nhất)
        2. Địa điểm
        3. Kinh nghiệm/Lương (chọn 1 trong 2)
        4. Hình thức làm việc
        
        Args:
            info_status: Trạng thái các thông tin (có/không có)
            
        Returns:
            List[InfoType]: Danh sách tối đa 2 thông tin cần hỏi thêm, theo thứ tự ưu tiên
        """
        priority_order = [
            InfoType.JOB_POSITION,
            InfoType.LOCATION,
            InfoType.EXPERIENCE,
            InfoType.SALARY,
            InfoType.WORK_TYPE
        ]
        
        missing_info = []
        for info_type in priority_order:
            if not info_status.get(info_type, False):
                missing_info.append(info_type)
                
        # Chỉ lấy tối đa 2 thông tin quan trọng nhất
        return missing_info[:2]

    def generate_follow_up_question(self, missing_info: List[InfoType]) -> str:
        """
        Tạo câu hỏi follow-up tự nhiên để thu thập thông tin thiếu.
        
        Args:
            missing_info: Danh sách thông tin cần thu thập
            
        Returns:
            str: Câu hỏi follow-up
        """
        if not missing_info:
            return "Mình đã có đủ thông tin để tìm việc phù hợp cho bạn!"
            
        if len(missing_info) == 1:
            # Chỉ thiếu 1 thông tin
            info_type = missing_info[0]
            question = self.question_templates[info_type][0]
            return f"Để tìm được việc phù hợp nhất, {question.lower()}"
            
        elif len(missing_info) == 2:
            # Thiếu 2 thông tin - hỏi thông tin quan trọng hơn trước
            primary_info = missing_info[0]
            secondary_info = missing_info[1]
            
            primary_question = self.question_templates[primary_info][0]
            
            # Tạo câu hỏi kết hợp tự nhiên
            if primary_info == InfoType.JOB_POSITION and secondary_info == InfoType.LOCATION:
                return f"Để tìm được việc phù hợp, bạn có thể cho mình biết muốn tìm vị trí gì và ở thành phố nào không?"
            elif primary_info == InfoType.JOB_POSITION and secondary_info == InfoType.EXPERIENCE:
                return f"Bạn muốn tìm việc ở vị trí nào và có bao nhiều năm kinh nghiệm?"
            else:
                return f"Để tìm được việc phù hợp nhất, {primary_question.lower()}"
        
        return "Bạn có thể chia sẻ thêm về vị trí công việc mà bạn quan tâm không?"


class UserContext:
    """Lưu trữ thông tin người dùng trong session để tránh hỏi lại."""
    
    def __init__(self):
        self.collected_info: Dict[InfoType, str] = {}
        self.original_question: str = ""
        self.conversation_history: List[str] = []
    
    def add_info(self, info_type: InfoType, value: str):
        """Thêm thông tin đã thu thập."""
        self.collected_info[info_type] = value
    
    def has_info(self, info_type: InfoType) -> bool:
        """Kiểm tra xem đã có thông tin này chưa."""
        return info_type in self.collected_info
    
    def get_complete_query(self) -> str:
        """Tạo câu truy vấn hoàn chình từ thông tin đã thu thập."""
        parts = []
        
        if InfoType.JOB_POSITION in self.collected_info:
            parts.append(f"tìm việc {self.collected_info[InfoType.JOB_POSITION]}")
        
        if InfoType.LOCATION in self.collected_info:
            parts.append(f"tại {self.collected_info[InfoType.LOCATION]}")
            
        if InfoType.EXPERIENCE in self.collected_info:
            parts.append(f"có {self.collected_info[InfoType.EXPERIENCE]} kinh nghiệm")
            
        if InfoType.SALARY in self.collected_info:
            parts.append(f"lương {self.collected_info[InfoType.SALARY]}")
            
        if InfoType.WORK_TYPE in self.collected_info:
            parts.append(f"{self.collected_info[InfoType.WORK_TYPE]}")
        
        return " ".join(parts)


# Sử dụng example
if __name__ == "__main__":
    enhancer = QuestionEnhancer()
    context = UserContext()
    
    # Test với câu hỏi incomplete
    incomplete_questions = [
        "Tìm việc ở đây",
        "Tôi muốn tìm việc lập trình",
        "Có việc làm ở Hà Nội không?",
        "Tìm việc lương cao"
    ]
    
    for question in incomplete_questions:
        print(f"\nCâu hỏi: '{question}'")
        info_status = enhancer.analyze_incomplete_question(question)
        missing_info = enhancer.get_priority_missing_info(info_status)
        follow_up = enhancer.generate_follow_up_question(missing_info)
        
        print(f"Thông tin thiếu: {[info.value for info in missing_info]}")
        print(f"Câu hỏi follow-up: {follow_up}")
