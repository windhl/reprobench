# TIME: Temporal-Sensitive Multi-Dimensional Instruction Tuning and Robust Benchmarking for Video-LLMs

Yunxiao Wang¹, Meng Liu², Wenqi Liu¹, Xuemeng Song³, Bin Wen⁴, Fan Yang⁴, Tingting Gao⁴, Di Zhang⁴, Guorui Zhou⁴, Liqiang Nie¹

¹Shandong University, ²Shandong Jianzhu University, ³City University of Hong Kong, ⁴Kuaishou Technology

{yunxiao.wang, liuwq}@mail.sdu.edu.cn {mengliu.sdu, sxmustc, nieliqiang}@gmail.com {wenbin, yangfan, lisize, zhangdi08, zhouguorui}@kuaishou.com

## Abstract

Video large language models have achieved remarkable performance in tasks such as video question answering, however, their temporal understanding remains suboptimal. To address this limitation, we curate a dedicated instruction fine-tuning dataset that focuses on enhancing temporal comprehension across five key dimensions. In order to reduce reliance on costly temporal annotations, we introduce a multi-task prompt fine-tuning approach that seamlessly integrates temporal-sensitive tasks into existing instruction datasets without requiring additional annotations. Furthermore, we develop a novel benchmark for temporal-sensitive video understanding that not only fills the gaps in dimension coverage left by existing benchmarks but also rigorously filters out potential shortcuts, ensuring a more accurate evaluation. Extensive experimental results demonstrate that our approach significantly enhances the temporal understanding of video-LLMs while avoiding reliance on shortcuts.

## Introduction

Recent advancements in video large language models (video-LLMs) (Tang et al. 2025; Cheng et al. 2025a) have demonstrated significant capabilities in video understanding and reasoning. In contrast to image large language models (image-LLMs) (Keye 2025; Xiaomi 2025), which focus on static visual content analysis, video-LLMs must capture dynamic visual information across frames. This demands robust temporal understanding, a critical research challenge that has garnered substantial attention in recent work (Cheng et al. 2025b; Song et al. 2025).

Despite efforts to enhance temporal understanding in video-LLMs (Cheng et al. 2024; Liu et al. 2024a), recent studies indicate that significant challenges remain in tasks requiring advanced temporal reasoning (Wang et al. 2024b; Xiao et al. 2025). These limitations can be attributed to the following primary factors: 1) Insufficient temporal instruction fine-tuning data. Current video instruction tuning datasets (Lin et al. 2024; Chen et al. 2024a) prioritize generalization across common scenarios rather than in-depth temporal comprehension. Although some approaches, such as AVicuna (Tang et al. 2024), generate temporal instruction tuning datasets through video splicing, their applicability remains limited to temporal localization due to the inherent constraints of this method. 2) Exploitation of data shortcuts. For instance, in determining a child's movement direction (e.g., the Dynamic dimension in Figure 3), models may rely on facial orientation instead of conducting a genuine temporal analysis of positional changes, leading to errors when videos are reversed. Notably, temporal benchmarks (Li et al. 2024; Liu et al. 2024b) are also affected by such shortcuts. Our experimental results (Figure 5) show that performance based on single random frames significantly surpasses random baselines, indicating that many questions can be resolved without true temporal reasoning, thereby overestimating model capabilities.

To address these challenges, we systematically enhance Video-LLMs' temporal understanding and evaluation through the following improvements. First, we construct a Temporal-sensItive Multi-dimEnsional (TIME) instruction-tuning dataset comprising 34,000 carefully curated samples across five key temporal dimensions (including Dynamic, Reasoning, Duration, Location, and Order), which serves as a valuable complement to existing general-purpose instruction-tuning datasets. These dimensions capture essential aspects of temporal reasoning, such as the dynamics of events over time and the capacity to predict future occurrences. Simultaneously, we implement rigorous data filtering to remove any potential data shortcuts that might undermine the effectiveness of model tuning. Second, to further mitigate limitations in data volume, we propose a Multi-Task Prompt tuning (MTP) framework that augments standard instruction tuning with two types of temporal-oriented self-supervised tasks: frame-level task to improve single-frame temporal understanding, and segment-level task to enhance cross-segment temporal understanding. As shown in Figure 1, fine-tuning with our approach results in substantial performance gains across most temporal benchmarks for the evaluated video-LLMs. Finally, we develop a robust Temporal-sensItive Multi-dimEnsional Benchmark (TIMEBench), which covers five dimensions of temporal evaluation and provides a more accurate measure of temporal understanding ability by filtering out potential data shortcuts through a carefully designed filtering mechanism. Experimental results validate the rigor of our evaluation benchmark.

In summation, our contributions are as follows:

- We construct a temporal-sensitive multi-dimensional instruction-tuning dataset intended to augment existing general instruction-tuning corpora, incorporating curated samples that specifically address temporal reasoning challenges in video data.
- We introduce a novel multi-task prompt-tuning approach that enhances existing instruction fine-tuning processes with two temporal-oriented self-supervised tasks.
- We propose a robust temporal-sensitive multi-dimensional benchmark that provides a more accurate measure of temporal understanding ability by filtering out potential data shortcuts.

**Figure 1:** Performance of four video-LLMs evaluated across six benchmarks. "+ Ours" suffix denotes models fine-tuned with our approach, achieving substantial improvements on all benchmarks. TIMEBench (TIMEB), MVBench (MVB), TempCompass (TC), and AutoEval-Video (AE-V) focus on temporal scenarios, whereas Video-MME (V-MME) and ActivityNet-QA (AN-QA) evaluate general performance.

**Figure 2:** Overall framework overview. Our approach comprises three key components: the TIME instruction tuning dataset, the multi-task prompt tuning approach, and the TIMEBench video temporal understanding benchmark. The top panel shows the data preparation flow for TIME and TIMEBench in three sub-steps. The bottom left illustrates the multi-task prompt tuning, where auxiliary temporal tasks are randomly interleaved with the original prompt, enabling the model to address additional temporal tasks alongside the main question. The bottom right displays the evaluation format in TIMEBench, with all questions in a multiple-choice format for objective evaluation.

## Temporal Sensitive Instruction Tuning

In this section, we present our approach to enhancing temporal understanding in video-LLMs through two key components: the construction of a temporally-sensitive instruction-tuning dataset and the development of a multi-task prompt fine-tuning strategy. These components are designed to augment the model's capacity for temporal reasoning across a wide range of video-related tasks.

### TIME Instruction Tuning Dataset

The limited performance of existing video-LLMs on temporally sensitive tasks can be largely attributed to the absence of a dedicated instruction-tuning dataset tailored for temporal contexts. To address this gap, we construct the TIME instruction-tuning dataset, aimed at enhancing the model's temporal comprehension capabilities.

**Dimension and Data Selection.** To improve temporal comprehension in video-LLMs, we draw insights from related fields such as video moment localization (Liu et al. 2023) and action anticipation (Hu et al. 2022). We identify tasks that emphasize temporal understanding and categorize temporal reasoning into five key dimensions, as shown in Figure 3. Each dimension is paired with a task designed to strengthen the model's temporal reasoning capabilities.

**Dynamic.** This dimension evaluates the model's ability to capture dynamic changes over time, specifically focusing on detecting the direction of object movement. Each video is cropped to highlight the unidirectional movement of a target object. Data is collected from the VidOR (Shang et al. 2019) dataset, originally designed for scene graph generation. To ensure unique identification, video segments containing more than two objects of the same category in a single frame are filtered out. The direction of the object's movement is determined by calculating the position of the center point of its bounding box.

**Reasoning.** This dimension evaluates the model's capacity to forecast future events from observed temporal sequences. Specifically, we focus on action anticipation, where the model predicts the subsequent action based on preceding actions. For this task, we leverage the Ego4D Goal-Step (Song et al. 2023) dataset, which provides annotations for goal-oriented hierarchical activities. In our framework, each step in the sequence is treated as an anticipatory action, while the earlier steps form the observation sequence. To ensure high-quality data, we filter out sequences with fewer than three steps and truncate those exceeding 15 steps. Additionally, only sequences with at least 50% of the steps marked as "essential" are retained to mitigate noise.

**Duration.** This dimension evaluates the model's ability to perceive and estimate the duration of events in unedited videos. We challenge the model to determine the length of specific events by categorizing them into one of three segments based on their relative duration within the video. For this task, we use a subset of ActivityNet Captions (Krishna et al. 2017) where events are divided into three parts according to their temporal span, and the model must correctly identify the appropriate category for each event.

**Location.** This dimension measures the model's capability to pinpoint precise temporal segments within a video by determining when a given event occurs, distinct from assessing its duration. To construct the dataset for this task, we extract a non-overlapping subset from ActivityNet Captions (Krishna et al. 2017) and uniformly partition each video into three intervals: start, middle, and end. Only activities that both begin and end within the same interval are selected, ensuring the model concentrates on accurately identifying temporal boundaries.

**Order.** This dimension assesses the model's ability to understand temporal event sequences by ordering actions accurately. Specifically, the model must arrange multiple non-overlapping actions in the sequence in which they occur. For this task, we use the Charades (Sigurdsson et al. 2016) dataset, partitioning each video into segments comprising three distinct actions performed sequentially. To ensure sequence diversity, segments with identical actions are filtered out so that each sequence consists of unique action types. To ensure sufficient adequate context, we filter out video clips with very short target activities. This step reduces the likelihood of the model erring due to insufficient observational context rather than a lack of temporal understanding.

**Figure 3:** Examples from the TIME dataset and the TIMEBench benchmark with data distribution across task types. These examples encompass five tasks that target the Dynamic, Reasoning, Duration, Location, and Order dimensions of temporal understanding. Ground-truth answers are highlighted in orange. In addition to multiple-choice questions, open-ended questions are also provided.

**Question and Answer Generation.** Since the original datasets lack pre-existing QA pairs, we generate them to build a comprehensive QA dataset. To maximize diversity, we partition the dataset into two parts: open-ended and multiple-choice QA.

**Open-ended QA.** 1) Question Generation: For each task, we manually create an example question and then use ChatGPT (OpenAI 2024) to generate 10 variations based on the task description and example. In questions derived from the VidOR (Shang et al. 2019), ActivityNet Captions (Krishna et al. 2017), and Ego4D Goal-Step (Song et al. 2023) datasets, placeholders are inserted and later replaced with specific target objects, activities, or goal descriptions. 2) Answer Generation: For Dynamic and Reasoning, the correct answer typically reflects the direction of movement or the action category. For Duration and Location, answers are derived from event-associated timestamps, while for Order, the answer is the chronological arrangement of three actions.

**Multiple-choice QA.** 1) Question Generation: We follow the similar process as for open-ended QA, but incorporate additional instructions and answer options. 2) Instruction Generation: For each task, we generate 10 extra instructional prompts using ChatGPT (OpenAI 2024). These prompts, inserted before the question, guide video-LLMs to select the correct option from a list of candidates. 3) Option Generation: For Dynamic, Duration, and Location, all possible answers are provided as options. For Order, random permutations of actions are used to avoid shortcuts based on visual or keyword co-occurrence. For Reasoning, incorrect options are sampled from other steps within the same goal to minimize dependence on co-occurrence relationships.

**Dataset Debiasing.** Prior studies (Tong et al. 2024; Yu et al. 2024; Zhang et al. 2022; Huang et al. 2024) have shown that multimodal language models are prone to biases arising from heuristics such as keyword co-occurrence and inherent distributional patterns in training data, which can lead to hallucinatory behavior in video-LLMs. For example, Otani et al. (Otani et al. 2020) observed that many video moment location datasets exhibit a temporal bias, with events predominantly occurring at the beginning of the video. Consequently, models may over-predict early events, achieving high accuracy on biased test sets without genuine temporal comprehension.

To mitigate these biases and foster a true understanding of temporal events, we implement the following debiasing strategies: 1) We initially conduct a manual verification of the content generated by ChatGPT (OpenAI 2024) to ensure its accuracy. Then, we ensure a balanced distribution of answers across both open-ended and multiple-choice QA formats. Specifically, for Dynamic, Duration, and Location, we maintain roughly equal counts of each answer type to prevent skewed representations. 2) For Reasoning and Order, we downsample frequently occurring actions to alleviate long-tailed distributions. 3) For Dynamic, we incorporate a reversed version of the video to discourage reliance on visual shortcuts, such as face or vehicle orientation. And 4) we carefully balance the distribution of questions and options across all temporal dimensions.

### Multi-task Prompt Tuning

Relying solely on fully annotated datasets for instruction tuning is inherently limited by annotation availability. While existing work (Lei et al. 2021; Wang et al. 2023; Sun et al. 2022) has introduced unsupervised tasks such as masked frame modeling to improve temporal understanding, these approaches are not directly applicable to fine-tuning video-LLMs. To overcome this limitation, we propose a multi-task prompt-tuning approach that incorporates two auxiliary tasks into existing instruction-tuning datasets without requiring additional annotations.

**Frame Index Prediction.** In this task, we randomly sample a frame from the original video and position it at the beginning of the sequence. A prompt is inserted before the original question to guide the model in predicting the correct position of the displaced frame. The modified question-answer structure is illustrated in the upper-right of Figure 4.

**Assigned VideoQA.** This task trains the model to identify the relevant video segments required to answer a given question, similar to the location task. Here, a randomly selected video from the dataset is concatenated with the original video, with the order of the videos randomized. Because the initial questions focus on video content descriptions without detailed location cues, explicit prompt instructions are provided to help the model discern the correct video, without dictating the proportion of the two videos. This setup is shown in the bottom-right of Figure 4.

In both tasks, the temporal content of the original video is minimally altered to ensure that the model can still accurately answer the original question. Moreover, as depicted in Figure 4, we employ Qwen2.5-72B (Team 2024), an open-source LLM with capabilities comparable to ChatGPT (OpenAI 2024), to identify QA pairs that involve temporal content. We refrain from adding new tasks to these pairs to avoid introducing errors from video modification. For each auxiliary task, 10 prompts are generated using ChatGPT (OpenAI 2024). Following the workflow in Figure 2, we tune the video-LLMs with these auxiliary tasks. Specifically, for samples without temporal content, one auxiliary task is randomly selected, the video and QA pair are modified accordingly, and then the video-LLMs are tuned on the rest of the dataset. This approach opens a new avenue for unsupervised instruction fine-tuning aimed at enhancing the temporal comprehension abilities of LLMs.

**Figure 4:** Illustration of our multi-task prompt tuning approach. The LLM first determines whether a sample contains a temporal description. Only samples lacking such descriptions are augmented with auxiliary tasks. In the frame index prediction task, a frame is randomly sampled from the sequence, and the model must restore its original position. In the assigned videoQA task, a randomly selected video is concatenated with the original, and the model needs to ignore the additional content to answer the original question.

## TIMEBench

In this section, we introduce TIMEBench, a novel benchmark designed to evaluate temporal understanding in video models, and compare it with existing benchmarks. TIMEBench comprehensively assesses the temporal reasoning capabilities of video models across five dimensions: Dynamic, Reasoning, Duration, Location, and Order. Following the pipeline illustrated in Figure 2, we systematically collect and filter data from diverse sources and generate multiple-choice questions for objective evaluation. This design not only mitigates data shortcuts but also extends the evaluation to a broader range of temporal aspects, setting TIMEBench apart from existing benchmarks.

### Benchmark Construction

As discussed previously, existing benchmarks often fall short of covering the five dimensions outlined in Section and are susceptible to shortcut issues. To overcome these shortcomings, we develop a benchmark that follows the data preparation and processing pipeline described in Section . The key differences are outlined below.

**Data Preparation.** We leverage diverse data sources to construct TIMEBench, ensuring robust evaluation on out-of-domain data. Although both Ego4D Goal-Step (Song et al. 2023) and EgoPlan (Chen et al. 2024b) originate from Ego4D (Grauman et al. 2022), we exclusively use the subset of EgoPlan sourced from Epic-Kitchens (Damen et al. 2022) to avoid domain overlap. For the Breakfast (Kuehne, Arslan, and Serre 2014), we use coarse-level annotations to avoid overly fine-grained action partitioning, which could impede the model's ability to distinguish actions. Furthermore, for TACoS (Regneri et al. 2013) and QVHighlights (Lei, Berg, and Bansal 2021), we apply random video cropping and generate question-answer options based on the new timestamps, thereby minimizing reliance on prior knowledge or fixed temporal context.

**QA generation.** Following the pipeline in Section , we construct QA pairs with an emphasis on multiple-choice formats to ensure objective evaluation. The evaluation prompt is defined as: "Answer with the option's letter from the given choices directly and only give the best option". A complete example is provided in the bottom right of Figure 2.

**Benchmark Debiasing.** Prior work (Tong et al. 2024) as demonstrated that current models often exploit data shortcuts rather than exhibiting true temporal comprehension. To address this, we utilize three advanced open-source multimodal LLMs, i.e., Qwen2-VL (Wang et al. 2024a), LLaVA-OneVision (Li et al. 2025), and MiniCPM-V 2.6 (Yao et al. 2024), as judge agents to evaluate the validity of QA pairs. Specifically, each question is based on a randomly selected frame from the video, and the models are tasked with answering using only that single frame. Given the limited temporal comprehension capabilities of current video-LLMs (Wang et al. 2024b; Li et al. 2024), we adopt a majority voting approach. If two or more judge models answer correctly based solely on a single sampled frame, this indicates potential shortcut reliance, and the corresponding QA pair is filtered out. The final benchmark is constructed from the remaining valid pairs, and resampling is performed to ensure a balanced distribution of answer options.

### Benchmark Comparison

To ensure the objectivity of our evaluation, we carefully debias the construction of TIMEBench. To assess the effectiveness of this approach, we conducted an experiment (see Figure 5) comparing the impact of potential biases across various benchmarks. In this experiment, we use the random prediction accuracy Acc_r as a baseline and report Acc_s and Acc_b for comparison. Acc_s represents the accuracy of VideoLLaMA 2 (Cheng et al. 2024) using a single video frame as input, while Acc_b corresponds to the blind setting where videos are replaced with fully black images.

The results clearly demonstrate that on MVBench (Li et al. 2024), TempCompass (Liu et al. 2024b), and AutoEval-Video (Chen et al. 2023), the Acc_b consistently surpasses Acc_r even in the absence of visual information. Moreover, with the addition of just one frame from the videos, Acc_s on these three benchmarks significantly exceeds both Acc_r and Acc_b, indicating that many questions in these benchmarks can be answered without relying on temporal information. In contrast, on TIMEBench, both Acc_s and Acc_b fall below Acc_r, with a small gap between them, indicating that TIMEBench is less prone to shortcut biases and offers a more rigorous evaluation of temporal understanding. It can be attributed to our meticulous data filtering and debiasing procedures.

**Figure 5:** Performance comparison of VideoLLaMA 2 (Cheng et al. 2024) on existing Benchmarks. Acc_s represents the predictions made using only a single frame, Acc_b denotes the accuracy when visual information is excluded, and Acc_r indicates random predictions.

## Experiments

**Experiment Settings.** For evaluation, we used TIMEBench and five additional benchmarks: MVBench (Li et al. 2024), TempCompass (Liu et al. 2024b) and AutoEval-Video (Chen et al. 2023), which are tailored for video temporal understanding, as well as Video-MME (Fu et al. 2025) and ActivityNet-QA (Yu et al. 2019), which serve as general benchmarks for video comprehension. To validate the effectiveness of our method, we fine-tuned Video-LLaVA (Lin et al. 2024), VideoLLaMA 2 (Cheng et al. 2024), ShareGPT4Video (Chen et al. 2024a) and InternVL 2.5 (Chen et al. 2024c) using our TIME dataset and our MTP approach[^1]. Specifically, for Video-LLaVA and VideoLLaMA 2, the entire parameters of the LLMs was fine-tuned, whereas for ShareGPT4Video and InternVL 2.5, we employed LoRA to fine-tuning. Except for ShareGPT4Video, the visual encoders were frozen for all models. Further details are in the supplementary material.

[^1]: For Video-LLaVA, VideoLLaMA 2 and ShareGPT4Video, we combined their respective original instruction datasets with our TIME dataset. In the case of InternVL 2.5, since the the original instruction dataset is unavailable, we directly fine-tuned the model using our TIME dataset on the pre-trained checkpoint.

**Performance Comparison.** As illustrated in Table 1, fine-tuning with our method leads to significant improvements for all video-LLMs across most benchmarks, especially on the four benchmarks that specifically assess video temporal understanding. Simultaneously, performance on the two general benchmarks remains stable or shows slight improvements, indicating that our method enhances temporal reasoning without compromising overall performance. Notably, the results on TIMEBench are closer to random performance, underscoring the stricter evaluation criteria of our benchmark in assessing temporal dimensions.

**Table 1:** Performance comparison across six benchmarks. The best performance for each part is highlighted in bold. TIMEBench, MVB, TC and AE-V focus on temporal scenarios, whereas V-MME and AN-QA address general scenario. TIMEBench, MVB and V-MME are multiple-choice forms, AE-V and AN-QA are open-ended forms, and TC contains both multiple-choice and open-ended forms.

| Model | LO | DU | DY | OR | RE | AVG | MVB | TC | AE-V | V-MME | AN-QA |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Random | 33.3 | 33.3 | 25.0 | 25.0 | 25.0 | 28.3 | 27.3 | 30.0 | 0.0 | 27.2 | 0.0 |
| Video-LLaVA | 32.7 | 32.3 | 22.8 | 26.5 | 24.8 | 27.3 | 42.8 | 51.9 | 9.8 | 30.3 | 37.8 |
| Video-LLaVA + Ours | 37.0 | 34.3 | 25.5 | 34.3 | 28.3 | 31.4 | 44.6 | 53.8 | 11.3 | 30.7 | 38.7 |
| VideoLLaMA 2 | 32.3 | 30.3 | 22.8 | 28.0 | 24.0 | 27.4 | 45.9 | 44.2 | 11.9 | 41.7 | 44.3 |
| VideoLLaMA 2 + Ours | 33.3 | 43.0 | 28.0 | 33.0 | 26.8 | 32.8 | 47.2 | 58.2 | 14.7 | 41.8 | 44.7 |
| ShareGPT4Video | 33.7 | 46.7 | 31.0 | 33.8 | 26.5 | 33.7 | 46.5 | 54.7 | 11.0 | 36.0 | 33.6 |
| ShareGPT4Video + Ours | 38.3 | 47.3 | 31.7 | 34.5 | 29.5 | 35.6 | 49.0 | 55.4 | 11.9 | 37.1 | 41.3 |
| InternVL 2.5 | 30.3 | 45.7 | 29.3 | 42.0 | 26.8 | 34.4 | 72.1 | 52.2 | 14.7 | 59.6 | 51.7 |
| InternVL 2.5 + Ours | 30.6 | 48.3 | 29.8 | 42.8 | 27.0 | 35.7 | 71.9 | 52.7 | 15.0 | 59.0 | 54.4 |

*Note: LO, DU, DY, OR, RE, AVG are the TIMEBench sub-scores (Location, Duration, Dynamic, Order, Reasoning, Average). MVB, TC, AE-V, V-MME, AN-QA are the five external benchmarks (MVBench, TempCompass, AutoEval-Video, Video-MME, ActivityNet-QA).*

**Ablation Study.** We conducted ablation experiments on VideoLLaMA 2 (Cheng et al. 2024) to dissect the contributions of our approach. Table 2 shows that both TIME and MTP independently improve the model's temporal understanding, while their combination achieves the best balance between temporal tasks and general tasks.

**Table 2:** Ablation study of TIME dataset and MTP method. The best performance is highlighted in bold, and the second-best result is indicated with underlines.

| Model | LO | DU | DY | OR | RE | AVG | MVB | TC | AE-V | V-MME | AN-QA |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 32.3 | 30.3 | 22.8 | 28.0 | 24.0 | 27.4 | 45.9 | 44.2 | 11.9 | 41.7 | 44.3 |
| + TIME | 34.3 | 41.0 | 26.5 | 34.8 | 26.3 | 32.6 | 47.1 | 57.4 | 14.0 | 41.6 | 44.6 |
| + MTP | 35.3 | 32.0 | 24.5 | 31.0 | 24.8 | 29.5 | 45.9 | 49.7 | 13.8 | 41.9 | 44.5 |
| + ALL | 33.3 | 43.0 | 28.0 | 33.0 | 26.8 | 32.8 | 47.2 | 58.2 | 14.7 | 41.8 | 44.7 |

In Table 3, we compared different strategies for integrating TIME data into the training process. Our findings indicate that mixing TIME data with the original instruction fine-tuning dataset concurrently yields superior performance compared to sequentially adding TIME data after or before the original fine-tuning. This improvement is likely due to mitigating the distribution gap between temporal tasks and general tasks by integrating them together.

**Table 3:** Ablation study on the strategy for incorporating the TIME dataset. The best performance is highlighted in bold, and the second-best result is indicated with underlines.

| Method | LO | DU | DY | OR | RE | AVG |
|---|---|---|---|---|---|---|
| Baseline | 32.3 | 30.3 | 22.8 | 28.0 | 24.0 | 27.4 |
| Mixing | 34.3 | 41.0 | 26.5 | 34.8 | 26.3 | 32.6 |
| After | 31.3 | 30.3 | 23.0 | 25.3 | 25.3 | 26.6 |
| Before | 34.2 | 35.3 | 23.3 | 29.8 | 24.0 | 28.7 |

Table 4 and Table 5 explore the impact of different proportions of auxiliary temporal tasks. We observe that introducing any proportion of auxiliary tasks improves performance on temporal tasks, confirming their effectiveness. However, increasing the proportion of auxiliary tasks beyond a certain threshold does not yield further improvements and may even degrade performance. Based on our experiments, the optimal mix is 50% assigned video question-answering tasks and 25% frame index prediction tasks.

**Table 4:** Ablation study on frame index prediction task ratio.

| Method | LO | DU | DY | OR | RE | AVG |
|---|---|---|---|---|---|---|
| 100% | 32.7 | 30.3 | 25.5 | 29.5 | 23.3 | 27.9 |
| 75% | 34.0 | 31.0 | 26.3 | 28.0 | 22.5 | 27.9 |
| 50% | 35.3 | 30.3 | 22.5 | 30.5 | 27.5 | 28.8 |
| 25% | 38.0 | 31.3 | 26.5 | 26.5 | 25.0 | 28.9 |
| 0% | 32.3 | 30.3 | 22.8 | 28.0 | 24.0 | 27.4 |

**Table 5:** Ablation study on the assigned videoQA task ratio.

| Method | LO | DU | DY | OR | RE | AVG |
|---|---|---|---|---|---|---|
| 100% | 35.0 | 35.3 | 25.3 | 32.0 | 25.4 | 30.1 |
| 75% | 36.7 | 31.0 | 26.3 | 30.8 | 24.3 | 29.3 |
| 50% | 34.3 | 41.0 | 27.5 | 32.8 | 25.5 | 31.6 |
| 25% | 33.7 | 30.7 | 26.8 | 29.5 | 23.8 | 28.5 |
| 0% | 32.3 | 30.3 | 22.8 | 28.0 | 24.0 | 27.4 |

**Qualitative Analysis.** Figure 6 compares the predictions of the original VideoLLaMA 2 (Cheng et al. 2024) and the fine-tuned version on two TIMEBench samples. In the Location example, the fine-tuned model better captures subtle temporal location differences, while in the Dynamic sample (with reversed video), the fine-tuned model relies less on priors like face orientation compared to the original model.

**Figure 6:** Visualization of partial sample prediction results in TIMEBench. The correct answer is highlighted in orange.

## Conclusion

In this work, we present a comprehensive framework to enhance temporal understanding in video-LLMs by delineating five key dimensions of temporal reasoning. Building on these dimensions, we introduced the TIME instruction fine-tuning dataset and a novel multi-task prompt-tuning approach that overcomes the limitations of traditional data labeling. Furthermore, our proposed TIMEBench benchmark exposes the temporal shortcomings of existing video-LLMs while validating the effectiveness of our approach in advancing temporal reasoning capabilities.
