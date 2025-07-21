# Chatbot Zalo với RAG

Một chatbot Zalo được tích hợp với Smax, sử dụng kỹ thuật Retrieval-Augmented Generation (RAG) để trả lời các câu hỏi của người dùng dựa trên một kho tài liệu được cung cấp.

## Tính năng chính

-   **Webhook Tích hợp Smax**: Nhận và xử lý tin nhắn từ người dùng Zalo thông qua webhook.
-   **Tạo sinh câu trả lời (RAG)**: Sử dụng mô hình ngôn ngữ kết hợp với cơ sở dữ liệu vector để tạo ra câu trả lời chính xác từ tài liệu nội bộ.
-   **Nạp dữ liệu động**: Cung cấp kịch bản để dễ dàng nạp và xử lý các tài liệu (định dạng `.md`, `.pdf`) vào vector store.
-   **Ghi log tin nhắn**: Tùy chọn webhook để ghi lại lịch sử tin nhắn vào Google Sheet.

## Yêu cầu

-   Python 3.8+
-   Tài khoản Smax để kết nối với Zalo OA.
-   API của OpenAI hoặc nhà cung cấp mô hình ngôn ngữ khác
-   Service Account của Google Cloud với quyền truy cập Google Sheets API

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

    Tạo một file `.env` trong thư mục gốc của dự án và thêm các biến sau:

    ```env
    # Bắt buộc: API key cho mô hình ngôn ngữ
    OPENAI_API_KEY="sk-..."

    # Tùy chọn: ID của Google Sheet để ghi log
    SPREADSHEET_ID="your-google-sheet-id"
    ```

    Nếu bạn sử dụng webhook để ghi log ra Google Sheet, hãy đảm bảo bạn có file `credentials.json` của Service Account trong thư mục dự án.

## Cách nạp dữ liệu (Ingest Data)

Để chatbot có thể trả lời câu hỏi, bạn cần cung cấp tài liệu cho nó.

1.  Đặt các file tài liệu (`.md`, `.pdf`, ...) vào thư mục `app/data`.

2.  Chạy kịch bản `ingest.py` và trỏ đến thư mục chứa dữ liệu:
    ```bash
    python ingest.py app/data
    ```
    Quá trình này sẽ đọc tài liệu, xử lý và lưu trữ chúng dưới dạng vector trong thư mục `app/vector_store`.

## Cách chạy dự án

### 1. Chạy Chatbot chính

Ứng dụng chính xử lý logic của chatbot.
```bash
python run.py
```
Ứng dụng sẽ chạy tại `http://localhost:8080`.

Bạn cần sử dụng một công cụ như `ngrok` để tạo một URL công khai và cấu hình nó làm webhook trong Smax.

-   **Endpoint chính**: `POST /webhook/smax`

### 2. (Tùy chọn) Chạy Webhook ghi log

Nếu bạn muốn ghi lại tất cả tin nhắn của người dùng vào Google Sheet:
```bash
python webhook_app.py
```
Ứng dụng này sẽ chạy trên một port khác (mặc định là 8080, bạn có thể cần chỉnh sửa để tránh xung đột nếu chạy cùng lúc).

-   **Endpoint ghi log**: `POST /webhook`

## Cấu trúc dự án

<pre>
chatbot_zalo/
├── app/
│   ├── data/                 # Chứa tài liệu nguồn (input)
│   ├── vector_store/         # Chứa cơ sở dữ liệu vector (output)
│   ├── services/             # Logic nghiệp vụ (RAG, Smax, OpenAI)
│   ├── main.py               # Ứng dụng FastAPI chính của chatbot
│   └── config.py             # Cấu hình
├── ingest.py                 # Kịch bản để nạp dữ liệu
├── run.py                    # Kịch bản để khởi chạy ứng dụng chính
├── webhook_app.py            # Ứng dụng phụ để ghi log ra Google Sheet
├── requirements.txt          # Danh sách thư viện
└── README.md                 # Tài liệu hướng dẫn
</pre> 