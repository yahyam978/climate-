try:
    search_results = Search(f"{query} chemical engineering").results
    filtered_videos = []
    
    for i, video in enumerate(search_results[:max_results*3]):
        progress = (i + 1) / min(max_results*3, len(search_results))
        progress_bar.progress(progress)
        status_text.text(f"جاري تحليل الفيديوهات... {int(progress*100)}%")
        
        try:
            yt = YouTube(video.watch_url)
            duration = yt.length
            
            if not (min_duration*60 <= duration <= max_duration*60):
                continue
            
            title = yt.title.lower()
            description = yt.description.lower() if yt.description else ""
            
            language = "other"
            if any(word in title+description for word in ["عرب", "arabic", "بالعربي", "شرح"]):
                language = "arabic"
            elif any(word in title+description for word in ["eng", "english", "lecture", "course"]):
                language = "english"
            elif any(word in title+description for word in ["hindi", "हिंदी"]):
                language = "hindi"
            
            egyptian_university = any(univ in title+description for univ in ["cairo", "جامعة القاهرة", "عين شمس", "alexandria", "الإسكندرية"])
            
            score = 0
            if language == "arabic":
                score += 3
            elif language == "english":
                score += 2
            elif language == "hindi":
                score += 1
            
            if egyptian_university:
                score += 2
            
            filtered_videos.append({
                "title": yt.title,
                "url": yt.watch_url,
                "duration": f"{duration//60}:{duration%60:02d}",
                "language": language,
                "egyptian": egyptian_university,
                "score": score,
                "thumbnail": yt.thumbnail_url
            })
            
        except Exception as e:
            continue
    
    filtered_videos.sort(key=lambda x: x["score"], reverse=True)
    
    if not filtered_videos:
        st.warning("لم يتم العثور على فيديوهات تطابق معاييرك.")
    else:
        st.success(f"تم العثور على {len(filtered_videos[:max_results])} فيديو تطابق معاييرك.")
        
        for i, video in enumerate(filtered_videos[:max_results]):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.image(video["thumbnail"], width=200)
            
            with col2:
                st.subheader(f"{i+1}. {video['title']}")
                st.markdown(f"""
                - **المدة:** {video['duration']} دقيقة
                - **اللغة:** {'عربية' if video['language'] == 'arabic' else 'إنجليزية' if video['language'] == 'english' else 'هندية'}
                - **من جامعة مصرية:** {'نعم' if video['egyptian'] else 'لا'}
                - [مشاهدة الفيديو]({video['url']})
                """)
            
            st.markdown("---")

except Exception as e:
    st.error(f"حدث خطأ أثناء البحث: {str(e)}")

progress_bar.empty()
status_text.empty()
