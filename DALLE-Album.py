from openai import OpenAI
import openai
import streamlit as st
import asyncio
import os

# セッション状態の初期化
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'selected_tags' not in st.session_state:
    st.session_state.selected_tags = set()
if 'api_type' not in st.session_state:
    st.session_state.api_type = 'なし'
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'base_prompt' not in st.session_state:
    st.session_state.base_prompt = "Create an album cover with the following style: "
# セッション状態の初期化部分に追加
if 'ordered_tags' not in st.session_state:
    st.session_state.ordered_tags = []

# 環境変数にAPIキーを設定
os.environ['OPENAI_API_KEY'] = st.session_state.api_key

# APIの設定
def configure_openai_api():
    if st.session_state.api_type == 'openai':
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = "https://api.openai.com/v1"
        openai.api_type = "openai"
    elif st.session_state.api_type == 'azure':
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = "https://YOUR_AZURE_OPENAI_ENDPOINT"  # Azure OpenAI Serviceのエンドポイント
        openai.api_version = "2022-12-01"  # 使用するAPIバージョン
        openai.api_type = "azure"

# API設定を呼び出し
configure_openai_api()

# 利用可能なタグ一覧
TAGS = [
    "ポップ", "ロック", "ジャズ", "クラシック", 
    "エレクトロニック", "アコースティック", "サイケデリック",
    "ミニマル", "レトロ", "モダン"
]

# update_prompt() 関数を修正
def update_prompt():
    base = st.session_state.base_prompt
    if ":" in base:
        base = base.split(":")[0] + ":"
    
    if st.session_state.ordered_tags:
        return f"{base} {', '.join(st.session_state.ordered_tags)}"
    return base

async def generate_image(prompt):
    if st.session_state.api_type == 'なし':
        return 'image.jpg'
    
    try:
        if st.session_state.api_type == 'OpenAI':
            # client = OpenAI()
            response = OpenAI().images.generate(
                model="dall-e-3",
                prompt="a white siamese cat",
                size="1024x1024",
                quality="standard",
                n=1,
            )

            return response.data[0].url
        elif st.session_state.api_type == 'Azure OpenAI Service':
            pass
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

def main():
    if st.session_state.page == 'settings':
        st.title('API設定')
        
        st.session_state.api_type = st.radio(
            "API種別を選択してください",
            ('なし', 'OpenAI', 'Azure OpenAI Service')
        )
        
        st.session_state.api_key = st.text_input(
            "API Key",
            type="password",
            disabled=(st.session_state.api_type == 'なし'),
            value=st.session_state.api_key
        )
        
        st.button('送信 or 戻る', on_click=lambda: setattr(st.session_state, 'page', 'main'))
            
    else:  # main page
        st.title('アルバムジャケット生成 beta')
        
        col1, col2 = st.columns([6, 1])
        with col2:
            st.button('API設定画面へ', on_click=lambda: setattr(st.session_state, 'page', 'settings'))
        
        # main() 関数内のプロンプト入力エリアの部分を修正
        # プロンプト入力エリア
        current_prompt = st.text_area("基本プロンプト", value=update_prompt(), key="prompt_area")
        # 基本プロンプト部分のみを保存
        if ":" in current_prompt:
            st.session_state.base_prompt = current_prompt.split(":")[0] + ":"
        else:
            st.session_state.base_prompt = current_prompt
        
        # タグ選択エリア
        st.write("スタイルタグを選択してください：")
        cols = st.columns(5)
        for i, tag in enumerate(TAGS):
            with cols[i % 5]:
                if st.button(
                    tag,
                    type="primary" if tag in st.session_state.selected_tags else "secondary",
                    key=f"tag_{tag}"
                ):
                    if tag in st.session_state.selected_tags:
                        st.session_state.selected_tags.remove(tag)
                        st.session_state.ordered_tags.remove(tag)
                    else:
                        st.session_state.selected_tags.add(tag)
                        st.session_state.ordered_tags.append(tag)
                    st.rerun()
        
        # 画像生成ボタン
        if st.button('生成'):
            with st.spinner('画像を生成中...'):
                image_url = asyncio.run(generate_image(current_prompt))
                if image_url:
                    if image_url == 'image.jpg':
                        st.image('images/image.jpg', caption='アルバムジャケット')
                    else:
                        st.image(image_url, caption='アルバムジャケット')

if __name__ == "__main__":
    main()