# Correction Rules (纠错规则与知识库)

## 1. 中文同音字/近音字错误 (Chinese Homophone Errors)
在日常交流中，常见的输入法同音字错误包括但不限于：
- 下在 -> 下载 (Download) [High Confidence]
- 代马 / 呆码 -> 代码 (Code) [High Confidence]
- 运型 -> 运行 (Run) [High Confidence]
- 报措 -> 报错 (Error) [High Confidence]
- 测是 -> 测试 (Test) [High Confidence]
- 不属 -> 部署 (Deploy) [High Confidence]

## 2. 英文拼写错误 (English Spelling Errors)
常见的英文单词拼写遗漏或错误：
- funciton -> function [High Confidence]
- recieve -> receive [High Confidence]
- defin -> define [High Confidence]
- enviroment -> environment [High Confidence]

## 3. 严重语义错误 (Severe Semantic Errors)
当出现大面积的音译、语音识别错误时，通常属于 **Low Confidence**，必须拦截确认。
- 拍森 -> Python
- 买色扣 -> MySQL
- 瑞阿克特 -> React
- 贾瓦 -> Java

## 4. 历史偏好与白名单推断 (Context & Whitelist Inference)
- **白名单优先**：在进行任何纠错前，必须比对 `assets/user_dictionary.json`。白名单中的词汇具有最高优先级，绝对不能被纠正。
- **代码上下文**：如果用户提到了当前项目不存在的词汇，但非常接近某个已有文件名、变量名，优先认为是拼写错误。