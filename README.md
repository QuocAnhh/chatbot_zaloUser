# Chatbot Zalo với RAG

Dự án này là một chatbot Zalo được tích hợp với Smax, sử dụng kỹ thuật Retrieval-Augmented Generation (RAG) để trả lời các câu hỏi của người dùng dựa trên một kho tài liệu được cung cấp.

## Tính năng chính

-   **Tích hợp Smax & Zalo**: Nhận và xử lý tin nhắn từ người dùng Zalo thông qua một webhook duy nhất.
-   **Tạo sinh câu trả lời (RAG)**: Sử dụng mô hình ngôn ngữ kết hợp với cơ sở dữ liệu vector để tạo ra câu trả lời chính xác từ tài liệu nội bộ.
-   **Ghi log tự động**: Tự động ghi lại toàn bộ lịch sử tin nhắn vào Google Sheet dưới dạng tác vụ nền (background task) mà không làm ảnh hưởng đến tốc độ phản hồi của chatbot.
-   **Nạp dữ liệu động**: Cung cấp kịch bản để dễ dàng nạp và xử lý các tài liệu (định dạng `.md`, `.pdf`) vào vector store.

## Yêu cầu

-   Python 3.11+
-   Tài khoản Smax và Zalo đã được kết nối.
-   API Token từ Smax.
-   API OpenAI hoặc nhà cung cấp mô hình ngôn ngữ khác.
-   Service Account của Google Cloud với quyền truy cập Google Sheets API và file `credentials.json`.

## Cài đặt

1.  **Clone repository:**
    ```bash
    git clone https://github.com/QuocAnhh/chatbot_zaloUser.git
    cd chatbot_zaloUser
    ```

2.  **Tạo và kích hoạt môi trường ảo:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Trên Windows: venv\Scripts\activate
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Cấu hình biến môi trường:**

    Tạo một file `.env` trong thư mục gốc của dự án và điền các giá trị tương ứng:

    ```env
    # API key cho mô hình ngôn ngữ (ví dụ: OpenAI, Gemini)
    OPENAI_API_KEY="sk-..."

    # API Token và Endpoint của Smax để gửi tin nhắn trả lời
    SMAX_API_TOKEN="your-smax-api-token-here"
    SMAX_API_ENDPOINT="https://smax.live/api/v2.1/me/live-chat/send-message"

    # ID của Google Sheet để ghi log
    SPREADSHEET_ID="your-google-sheet-id"
    ```
    **Lưu ý:** Đảm bảo bạn đã đặt file `credentials.json` của Google Service Account vào thư mục gốc của dự án.

## Cách nạp dữ liệu (Ingest Data)

Để chatbot có thể trả lời câu hỏi, bạn cần cung cấp tài liệu cho nó.

1.  Đặt các file tài liệu (`.md`, `.pdf`, ...) vào thư mục `app/data`.

2.  Chạy kịch bản `ingest.py` và trỏ đến thư mục chứa dữ liệu:
    ```bash
    python ingest.py app/data
    ```
    Quá trình này sẽ đọc tài liệu, xử lý và lưu trữ chúng dưới dạng vector trong thư mục `app/vector_store`.

## Cách chạy dự án

Khởi chạy ứng dụng duy nhất bằng lệnh:
```bash
python run.py
```
Ứng dụng sẽ chạy tại `http://localhost:8080` và xử lý đồng thời cả logic chatbot và việc ghi log.

Bạn cần sử dụng một công cụ như `ngrok` để tạo một URL công khai và cấu hình nó làm webhook trong Smax.

-   **Endpoint duy nhất**: `POST /webhook/smax`

## Cấu trúc dự án

<pre>
chatbot_zalo/
├── app/
│   ├── data/                 # Chứa docs nguồn (input)
│   ├── vector_store/         # Chứa db vector (output)
│   ├── services/             # logic nghiệp vụ (RAG, Smax, OpenAI, Google Sheets)
│   ├── main.py               # FastAPI (webhook, chatbot, logging)
│   └── config.py             # Cấu hình
├── ingest.py                 # nạp dữ liệu
├── run.py                    # chạy ứng dụng
├── requirements.txt          # list thư viện
├── .env                      # chứa các biến môi trường (cần tự tạo)
└── README.md                 # instruction
</pre> 