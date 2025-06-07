import streamlit as st
from pytube import YouTube, Search
import time

st.set_page_config(page_title="Chemical Engineering YouTube Search", layout="wide")
st.title("Chemical Engineering YouTube Search Engine")
st.markdown("""
<style>
.arabic {
    direction: rtl;
    text-align: right;
    font-family: 'Arial', sans-serif;
}
</style>
""", unsafe_allow_html=True)

with st.form("search_form"):
    query = st.text_input("Enter search topic:")
    max_results = st.slider("Number of results to show", 5, 20, 10)
    min_duration = st.slider("Minimum video duration (minutes)", 1, 30, 10)
    max_duration = st.slider("Maximum video duration (minutes)", 10, 120, 60)
    submitted = st.form_submit_button("Search")

if submitted and query:
    st.subheader(f"Search results for: '{query}'")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        search_results = Search(f"{query} chemical engineering").results
        filtered_videos = []
        
        for i, video in enumerate(search_results[:max_results*3]):
            progress = (i + 1) / min(max_results*3, len(search_results))
            progress_bar.progress(progress)
            status_text.text(f"Analyzing videos... {int(progress*100)}%")
            
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
            st.warning("No videos found matching your criteria.")
        else:
            st.success(f"Found {len(filtered_videos[:max_results])} videos matching your criteria.")
            
            for i, video in enumerate(filtered_videos[:max_results]):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.image(video["thumbnail"], width=200)
                
                with col2:
                    st.subheader(f"{i+1}. {video['title']}")
                    st.markdown(f"""
                    - **Duration:** {video['duration']} minutes
                    - **Language:** {'Arabic' if video['language'] == 'arabic' else 'English' if video['language'] == 'english' else 'Hindi'}
                    - **From Egyptian University:** {'Yes' if video['egyptian'] else 'No'}
                    - [Watch Video]({video['url']})
                    """)
                
                st.markdown("---")
    
    except Exception as e:
        st.error(f"Error during search: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()

st.sidebar.header("Usage Instructions")
st.sidebar.write("""
1. Enter your search topic in the text field
2. Adjust the number of results to show
3. Set minimum and maximum video duration
4. Click the Search button to see results
""")
st.sidebar.header("Ranking Criteria")
st.sidebar.write("""
- Priority for Arabic videos
- Then English videos
- Then Hindi videos
- Videos from Egyptian universities get bonus points
""")
