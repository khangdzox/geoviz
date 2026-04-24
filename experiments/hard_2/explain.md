# Explanation of files in hard_2 experiment

* `chatgpt_1.py`: initial attempt with ChatGPT
* `chatgpt_2_chaining.py`: second attempt with prompt-chaining technique with ChatGPT. Unfinished.
* `chatgpt_3_revised.py`: third attempt with ChatGPT, use revised prompt
* `claude.py`: attempt with Claude API (claude-sonnet-4-6, temperature=0.6, thinking=disabled, effort=high)

# Problem

Vietnamese:

Cho tam giác ABC có ba góc nhọn (AB < AC), nội tiếp đường tròn (O). Đường cao AD của tam giác ABC cắt đường tròn (O) tại điểm E (E khác A). Gọi K là chân đường vuông góc kẻ từ điểm E đến đường thẳng AB.  
a) Chứng minh bốn điểm E, D, B, K cùng thuộc một đường tròn.  
b) Đường thẳng AO cắt đường thẳng BC tại điểm S. Chứng minh EA là tia phân giác của góc CEK và AB.AC = AE.AS.  
c) Gọi H là trực tâm của tam giác ABC và I là trung điểm của đoạn thẳng AB. Chứng minh đường thẳng SI vuông góc với đường thẳng HK.

English:

Given an acute triangle ABC (AB<AC) inscribed in the circumcircle (O). The altitude AD of triangle ABC intersects the circumcircle (O) again at point E (E/=A). Let K be the foot of the perpendicular from point E to line AB.  
a) Prove that the four points E,D,B,K are concyclic.  
b) The line AO intersects line BC at point S. Prove that EA is the angle bisector of ∠CEK and that AB⋅AC=AE⋅AS.  
c) Let H be the orthocenter of triangle ABC and I be the midpoint of segment AB. Prove that line SI is perpendicular to line HK.
