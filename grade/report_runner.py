"""
IELTS Speaking Report Runner
将report.ipynb中的评分功能转换为可执行的Python脚本
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Optional, Any

# 设置路径
GRADE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_OUTPUT_DIR = os.path.join(os.path.dirname(GRADE_DIR), "web_output")

class IeltsSpeakingEvaluator:
    """雅思口语评分系统，通过调用大语言模型API生成评分报告"""
    
    def __init__(self, api_key: str, api_base_url: str, model_name: str = "gpt-3.5-turbo"):
        """
        初始化评分器
        
        :param api_key: 大语言模型API密钥
        :param api_base_url: API基础地址
        :param model_name: 模型名称
        """
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.model_name = model_name
        self.ielts_criteria = self._load_ielts_criteria()
        
    def _load_ielts_criteria(self) -> str:
        """加载雅思口语评分标准"""
        return """雅思口语评分标准分为四个维度，每个维度0-9分：
1. 流利度与连贯性 (Fluency and Coherence)
   - 包括语言表达的流畅程度、停顿的自然性、逻辑连接词的使用
   - 能否有条理地组织观点，能否持续表达较长的内容

2. 词汇多样性 (Lexical Resource)
   - 词汇量大小、词汇使用的准确性和恰当性
   - 能否使用同义替换、是否有词汇错误

3. 语法多样性与准确性 (Grammatical Range and Accuracy)
   - 语法结构的多样性、复杂句的使用能力
   - 语法错误的频率和严重程度

4. 发音 (Pronunciation)
   - 发音的清晰度、重音、语调和节奏
   - 能否被理解，是否有系统性发音问题

评分描述：
- 9分：接近母语者水平
- 7-8分：良好水平，能有效沟通，有少量错误
- 5-6分：基础沟通能力，有明显错误但不影响理解
- 4分及以下：沟通能力有限，错误较多影响理解
"""
    
    def _create_prompt(self, part1: Dict, part2: Dict, part3: Dict, pronunciation_feedback: str) -> str:
        """
        创建提示词
        
        :param part1: 第一部分题目和回答
        :param part2: 第二部分题目和回答
        :param part3: 第三部分题目和回答
        :param pronunciation_feedback: 发音评价
        :return: 完整提示词
        """
        prompt = f"""请根据以下信息，按照雅思口语评分标准，为学生生成一份详细的评分报告。

雅思口语评分标准：
{self.ielts_criteria}

考试内容：
第一部分 (Part 1)：
题目：{part1['question']}
学生回答：{part1['answer']}

第二部分 (Part 2)：
题目：{part2['question']}
学生回答：{part2['answer']}

第三部分 (Part 3)：
题目：{part3['question']}
学生回答：{part3['answer']}

发音评价：{pronunciation_feedback}

请生成包含以下内容的评分报告：
1. 总体评分（0-9分）及简要评价
2. 四个评分维度的具体得分和详细分析，发音部分给出具体哪个单词没有发准
3. 优势和不足
4. 改进建议

报告格式应清晰易读，语言专业但易懂。
"""
        return prompt
    
    def _call_api(self, prompt: str) -> Optional[str]:
        """
        调用大语言模型API
        
        :param prompt: 提示词
        :return: API返回结果或None
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一位专业的雅思口语考官，擅长根据雅思评分标准进行公正、准确的评分。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # 降低随机性，提高评分一致性
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                data=json.dumps(data)
            )
            
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"API调用失败: {e}")
            return None
        except KeyError as e:
            print(f"API返回格式错误: {e}")
            return None
    
    def generate_report(self, part1: Dict, part2: Dict, part3: Dict, pronunciation_feedback: str, 
                        max_retries: int = 3) -> Optional[str]:
        """
        生成雅思口语评分报告
        
        :param part1: 第一部分题目和回答，格式: {'question': ..., 'answer': ...}
        :param part2: 第二部分题目和回答，格式同上
        :param part3: 第三部分题目和回答，格式同上
        :param pronunciation_feedback: 发音评价文本
        :param max_retries: 最大重试次数
        :return: 评分报告或None
        """
        prompt = self._create_prompt(part1, part2, part3, pronunciation_feedback)
        
        for attempt in range(max_retries):
            report = self._call_api(prompt)
            if report:
                return report
            if attempt < max_retries - 1:
                print(f"重试中... (第 {attempt + 2} 次尝试)")
                time.sleep(2 ** attempt)  # 指数退避
            
        return None


def load_ielts_data_from_files(
    part1_question_file,
    part1_answer_file,
    part2_question_file,
    part2_answer_file,
    part3_question_file,
    part3_answer_file
):
    """读取txt文件并返回内容"""
    def read_txt_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()

    # 加载Part1数据
    part1_data = {
        "question": read_txt_file(part1_question_file),
        "answer": read_txt_file(part1_answer_file)
    }

    # 加载Part2数据
    part2_data = {
        "question": read_txt_file(part2_question_file),
        "answer": read_txt_file(part2_answer_file)
    }

    # 加载Part3数据
    part3_data = {
        "question": read_txt_file(part3_question_file),
        "answer": read_txt_file(part3_answer_file)
    }

    return {
        "part1_data": part1_data,
        "part2_data": part2_data,
        "part3_data": part3_data
    }


def run_ielts_report(api_key=None, api_base_url=None, model_name=None, verbose=True):
    """
    运行IELTS评分报告生成
    
    Args:
        api_key: API密钥，如果为None则使用默认值
        api_base_url: API基础URL，如果为None则使用默认值
        model_name: 模型名称，如果为None则使用默认值
        verbose: 是否打印详细信息
    
    Returns:
        bool: 是否成功生成报告
    """
    try:
        # 检查必要文件是否存在
        required_files = {
            "part1_question": os.path.join(GRADE_DIR, "ielts_data", "Part1_q"),
            "part1_answer": os.path.join(GRADE_DIR, "ielts_data", "Part1_a"),
            "part2_question": os.path.join(WEB_OUTPUT_DIR, "part2_question.txt"),
            "part2_answer": os.path.join(WEB_OUTPUT_DIR, "part2_answer_transcript.txt"),
            "part3_question": os.path.join(WEB_OUTPUT_DIR, "part3_questions.txt"),
            "part3_answer": os.path.join(WEB_OUTPUT_DIR, "part3_answers.txt"),
            "pronunciation_score": os.path.join(WEB_OUTPUT_DIR, "pronunciation_score.json")
        }
        
        for name, file_path in required_files.items():
            if not os.path.exists(file_path):
                if verbose:
                    print(f"错误: 找不到{name}文件: {file_path}")
                return False
        
        # 设置API参数
        if api_key is None:
            api_key = "sk-40983a0291ec456c8ea66fec651667a4"  # 默认API密钥
        
        if api_base_url is None:
            api_base_url = "https://api.deepseek.com"  # 默认API基础URL
        
        if model_name is None:
            model_name = "deepseek-chat"  # 默认模型名称
        
        # 初始化评分器
        evaluator = IeltsSpeakingEvaluator(
            api_key=api_key,
            api_base_url=api_base_url,
            model_name=model_name
        )
        
        # 从文件加载数据
        data = load_ielts_data_from_files(
            part1_question_file=required_files["part1_question"],
            part1_answer_file=required_files["part1_answer"],
            part2_question_file=required_files["part2_question"],
            part2_answer_file=required_files["part2_answer"],
            part3_question_file=required_files["part3_question"],
            part3_answer_file=required_files["part3_answer"]
        )
        
        part1_data = data["part1_data"]
        part2_data = data["part2_data"]
        part3_data = data["part3_data"]
        
        # 读取发音评价
        with open(required_files["pronunciation_score"], 'r', encoding='utf-8') as f:
            pronunciation_feedback = f.read()
        
        # 生成报告
        if verbose:
            print("正在生成雅思口语评分报告...")
        
        report = evaluator.generate_report(
            part1=part1_data,
            part2=part2_data,
            part3=part3_data,
            pronunciation_feedback=pronunciation_feedback
        )
        
        if report:
            # 将报告保存到web_output目录
            report_path = os.path.join(WEB_OUTPUT_DIR, "ielts_speaking_report.txt")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            if verbose:
                print("雅思口语评分报告:")
                print("=" * 50)
                print(report)
                print("=" * 50)
                print(f"报告已保存到 {report_path}")
            
            return True
        else:
            if verbose:
                print("无法生成评分报告，请检查API配置和网络连接")
            return False
            
    except Exception as e:
        if verbose:
            print(f"生成报告时出错: {str(e)}")
            import traceback
            traceback.print_exc()
        return False


if __name__ == "__main__":
    # 从命令行参数获取API信息
    import argparse
    
    parser = argparse.ArgumentParser(description='生成IELTS口语评分报告')
    parser.add_argument('--api_key', help='API密钥')
    parser.add_argument('--api_base_url', help='API基础URL')
    parser.add_argument('--model_name', help='模型名称')
    parser.add_argument('--quiet', action='store_true', help='安静模式，不打印详细信息')
    
    args = parser.parse_args()
    
    # 运行报告生成
    success = run_ielts_report(
        api_key=args.api_key,
        api_base_url=args.api_base_url,
        model_name=args.model_name,
        verbose=not args.quiet
    )
    
    # 设置退出代码
    sys.exit(0 if success else 1)



