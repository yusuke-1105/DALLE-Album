from openai import OpenAI, AzureOpenAI
import streamlit as st
from PIL import Image
import requests
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
if 'resource_name' not in st.session_state:
    st.session_state.resource_name = ''
if 'base_prompt' not in st.session_state:
    st.session_state.base_prompt = "Create an album cover with the following style: "
# セッション状態の初期化部分に追加
if 'ordered_tags' not in st.session_state:
    st.session_state.ordered_tags = []
if 'prompt_area' not in st.session_state:
    st.session_state.number = 1

# 環境変数にAPIキーを設定
os.environ['OPENAI_API_KEY'] = st.session_state.api_key
os.environ['AZURE_OPENAI_API_KEY'] = st.session_state.api_key
os.environ['AZURE_OPENAI_ENDPOINT'] = st.session_state.resource_name

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
            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            return response.data[0].url
        elif st.session_state.api_type == 'Azure OpenAI Service':
            # Azure OpenAI Service client setup
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
                api_version="2024-02-01",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            return response.data[0].url
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# 古い画像の下部に新しい画像を繋ぎ合わせる
def append_images(image):
    try:
        roll_image = Image.open('roll_images/image.jpg')
        width, height = roll_image.size
        result = Image.new('RGB', (width, height + image.size[1]))
        result.paste(roll_image, (0, 0))
        result.paste(image, (0, height))
        result.save('roll_images/image.jpg')
        return
    except:
        image.save('roll_images/image.jpg')
        return

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

        st.session_state.resource_name = st.text_input(
            "Azure OpenAI Serviceのエンドポイント",
            disabled=(st.session_state.api_type != 'Azure OpenAI Service'),
            value=st.session_state.resource_name
        )
        
        st.button('送信 or 戻る', on_click=lambda: setattr(st.session_state, 'page', 'main'))
            
    else:  # main page
        st.title('アルバムジャケット生成 beta')
        
        _, col2 = st.columns([6, 1])
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
                        image = Image.open('images/image.jpg')
                        st.image(image, caption='アルバムジャケット')
                        image.save(f'images_{st.session_state.number}/image.jpg')
                        st.session_state.number = st.session_state.number % 2 + 1
                        append_images(image)
                    else:
                        image = Image.open(requests.get(image_url, stream=True).raw)
                        st.image(image, caption='アルバムジャケット')
                        image.save(f'images_{st.session_state.number}/image.jpg')
                        st.session_state.number = st.session_state.number % 2 + 1
                        append_images(image)
                        

if __name__ == "__main__":
    main()