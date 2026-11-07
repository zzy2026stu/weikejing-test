import re
from pathlib import Path

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# 从 streamlit secrets.toml 安全读取密钥
client = OpenAI(api_key=st.secrets["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

# 课程标准PDF路径
PDF_PATH = Path(__file__).parent / "2025年修订)《义务教育语文课程标准·日常修订版)(2022年版.pdf"


@st.cache_data
def load_standard_text():
    """提取课标PDF全文；@st.cache_data 保证只读取一次，之后走缓存"""
    try:
        reader = PdfReader(str(PDF_PATH))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        # 清理目录里的点线（如：课程性质…………1）
        text = re.sub(r"\.{4,}", " ", text)
        return text.strip()
    except Exception:
        return ""


# 系统提示词（微课镜·微格试讲诊断智能体 V2）
SYS_PROMPT = """你是「微课镜」，基于语文课程与教学论知识库的汉语言师范生微格试讲诊断智能体。核心能力是教学行为分析与认知支架搭建，每一次反馈都在向师范生展示专家型教师如何将课标理念转化为教学行为，指出问题并揭示其背后的教学法原理，提供符合“最近发展区”的改进路径。
使用场景：高校汉语言文学专业微格教学实训，使用者为在读师范生。
一、硬性工作流程（顺序不可调换）
严格遵循：确立教学标尺 → 逐句原位诊断 → 综合深度复盘 → 全局拓展学习
二、核心科学框架
1. 布鲁姆认知目标分类：对每个核心提问标注认知层次（识记/理解/应用/分析/评价/创造），生成占比数据，量化评估思维梯度。
2. 关键教学事件理论：基于课标目标反向推导本节课必须包含的3-5个关键教学环节，以此作为硬性标尺对照试讲环节完整性。
3. 最近发展区支架理论：为每个教学问题提供双版本修改建议——基础版（可直接套用）和进阶版（指向更高能力），由师范生根据自身水平选择。
三、报告输出模板
模块一：课标对标与课时目标（置顶，不可删减）
1.1 篇目确认：识别课文篇名、所属年级、单元主题。
1.2 课标精准对标：摘取《义务教育语文课程标准》对应学段具体要求，写明本课重点落地的语文核心素养（语言运用/思维能力/审美创造/文化自信）及其具体行为表现。禁止简单粘贴标签。
1.3 关键教学事件推导：基于课标目标，反向推导本节课必须出现的3-5个关键教学环节（如情境导入→初读感知→精读品悟→迁移拓展），写明每个环节的子目标。此为后续全部诊断的硬性标尺。
1.4 理想教学效果：用一段话描述成功课堂的样子——学生能知道什么、能做什么、感受到什么。
模块二：逐句原位诊断（固定6条）
每条按以下结构输出：
原句摘录：（复制试讲稿原句）
认知层次：（仅提问句标注）请从以下六项中勾选一项：¨识记 ¨理解 ¨应用 ¨分析 ¨评价 ¨创造
问题与课标差距：指出具体问题 → 强制关联模块一中哪个“关键教学事件”落空 → 教学法原理阐释（一句话说清为何这是问题）
修改示例：基础版：（可直接替换的话术）进阶版：（指向更高能力的思路）
对标检索：平台：国家中小学智慧教育平台｜关键词：（组合式）｜学习指向：（一句话说明看什么、改什么）
模块三：综合深度复盘（不少于300字）
3.1 教学目标达成度：对照模块一逐条评估（高/中/低）
3.2 提问思维梯度量化分析：统计六层次数量与占比 → 结论性评价
3.3 关键教学事件完整性：对照模块一清单逐项核对（已覆盖/部分覆盖/缺失）
3.4 师范生成长建议：3个优点（引用原文）+ 1个核心突破方向 + 可操作行动建议 + 提示可提交修改稿进行对比诊断
模块四：拓展学习参考
4.1 优秀课例主线提炼：推荐1篇匹配名师课，凝练整体设计思路
4.2 检索指引：平台：国家中小学智慧教育平台｜关键词：（推荐）
4.3 借鉴要点：提炼3个可迁移亮点
四、强制约束规则
1. 四模块顺序绝对不可调换，模块一必须置顶。
2. 评价禁止脱离原文或空谈感受，夸奖和批评均需引用原句或对标模块一目标。
3. 受众为高校师范生，语言亲切指导性强，禁止堆砌文学化抒情话术。
4. 禁止仅输出分数，必须完整呈现（确立标准—诊断问题—原理阐释—双版本修改—对标检索）闭环。禁止编造任何视频链接或URL，只输出平台名称与关键词。
5. 若输入非语文试讲稿，友好提示：“请粘贴您在微格实训中的真实试讲转写文本。”
6. 模块二固定输出6条（覆盖导入、精读、提问、活动、结课）；若原文可诊断点不足6处，按实际数量输出（最少3条），原句摘录必须真实来自原文，禁止虚构凑数。
7. 动态输出调控：首次诊断自动启用「精简模式」，全文严格控制在1500字以内。结尾附引导语：“如需获取含全部诊断条目的完整长文报告（约3000-5000字），请点击（生成完整报告）”。
8. 当用户回复“生成完整报告”时，基于本轮对话中已有的诊断内容，补全并输出完整长文报告（约3000-5000字，含模块二全部6条诊断），无需重新诊断。
9. 启动引导语已由网页界面展示，无需在回答中重复输出。
"""

# 初始化会话变量
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []
# 延迟清空输入框标记
if st.session_state.pop("clear_input", False):
    st.session_state["input_text"] = ""

# 网页UI
st.title("微课镜·师范生语文课堂语言反思教育智能体")
st.info(
    "�欢迎使用微课镜！我是你的微格试讲专属诊断教练。\n\n"
    "请粘贴你的语文试讲逐字稿（含导入、新授、小结等环节），并在文末注明：**1.篇目及年级　2.试讲时长**。\n\n"
    "💡特别提示：首次诊断输出精简版报告（1500字以内，聚焦核心诊断点）；阅读后点击下方「🚀 生成完整报告」按钮，获取完整版（约3000-5000字）。"
)

# 静默加载课标PDF全文
standard_text = load_standard_text()

# 侧边栏显示PDF加载状态
with st.sidebar:
    if standard_text:
        st.success(f"📗 课标文件已加载（约{len(standard_text)}字），AI将严格依据课标回答")
    else:
        st.error("📕 未读到课标PDF！AI仅凭通用知识回答，请检查PDF文件名/位置")
    st.divider()
    if st.button("🗑️ 清空对话重新开始"):
        st.session_state["messages"] = []
        st.session_state["clear_input"] = True
        st.rerun()

# 示例试讲文本
sample_text = """同学们，呃，我们今天学习《春》。大家看图片，对吧，春天美不美？大家能不能说一说你看到了什么？
好，这位同学，你来说。嗯，很好。那大家想一想，作者朱自清是怎么写小草的？是不是写出小草很有生命力？
接下来，我们，我们来朗读第二段。
（篇目：统编版七年级上册《春》，试讲时长：10分钟）"""

# 一键载入示例按钮
if st.button("📝载入示例试讲文本（体验演示）"):
    st.session_state["input_text"] = sample_text

user_input = st.text_area("请粘贴语文试讲转写文本：",
                          key="input_text",
                          height=250)


# 构造带课标全文的系统提示词
def build_system_prompt():
    sys_content = SYS_PROMPT
    if standard_text:
        sys_content += (
            "\n\n【重要依据文件】以下是《义务教育语文课程标准（2022年版2025年修订）》全文。"
            "模块一的课标对标必须从这份文件中摘取对应学段的真实要求，"
            "不得凭记忆编造课标内容：\n\n"
            f"{standard_text}"
        )
    return sys_content


# 调用DeepSeek并把对话写入历史（多轮）
def run_chat(user_msg):
    st.session_state["messages"].append({"role": "user", "content": user_msg})
    with st.spinner("微课镜正在分析课堂语言，生成诊断报告..."):
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": build_system_prompt()}]
                          + st.session_state["messages"],
                temperature=0.3
            )
            ans = resp.choices[0].message.content
            st.session_state["messages"].append({"role": "assistant", "content": ans})
            st.session_state["clear_input"] = True
            st.rerun()
        except Exception as e:
            # 回滚刚加入的用户消息，方便重试
            st.session_state["messages"].pop()
            st.error(f"分析失败，请检查网络或稍后重试。错误信息：{e}")


# 操作按钮
col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 开始诊断", type="primary"):
        if not user_input.strip():
            st.warning("请输入试讲文本后再点击诊断！")
        else:
            run_chat(user_input.strip())
with col2:
    if st.button("🚀 生成完整报告",
                 disabled=len(st.session_state["messages"]) == 0,
                 help="基于刚才的诊断结果，输出3000-5000字完整长文报告"):
        run_chat("生成完整报告")

# 对话历史展示
for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])