# AI-01 — helper structured output

Scope: instruksi PM 8 Oktober 2026, fondasi backend OpenAI tanpa endpoint atau UI.
Model tetap `gpt-6-luna`. Helper tidak terkait engine prediksi finansial F-02.

Install dependency backend dari `backend/requirements.lock`. Isi `AI_KEY` di
environment server, root `.env.local`, atau root `.env` (urutan prioritas itu).
Nilai kosong eksplisit dianggap belum dikonfigurasi, bukan fallback ke key lain.
Jangan memakai prefix `NEXT_PUBLIC_`. File rahasia tidak masuk Git.
Import helper tidak melakukan request; key baru diperiksa saat dipanggil.

```python
from backend.ai import AIError, generate_structured

schema = {
    "type": "object",
    "properties": {"summary": {"type": "string"}},
    "required": ["summary"],
    "additionalProperties": False,
}

# Di dalam fungsi async backend:
result = await generate_structured(
    "Ringkas teks ini: aplikasi membantu membaca data historis.",
    schema,
)
print(result["summary"])
```

Schema menentukan bentuk output; prompt tetap dibutuhkan untuk menentukan tugas
dan data masukan. Parameter opsional: `instructions` dan `max_output_tokens`
(default 4096, termasuk reasoning). Gunakan schema strict OpenAI: seluruh field
object wajib `required`, `additionalProperties: false`; field opsional dapat
memakai tipe nullable. Helper tidak mengubah schema diam-diam. Validasi JSON
Schema dilakukan lokal, tetapi subset yang didukung OpenAI diperiksa provider;
schema yang tidak didukung dapat menghasilkan HTTP 400.

Return berupa dict yang sudah diperiksa terhadap schema. `ValueError` berarti
input lokal tidak valid. `AIError` berarti key kosong, HTTP/network error,
refusal, respons belum selesai, atau output tidak valid. Pesan error tidak memuat
key, prompt, atau body respons provider. Caller dapat menangani error ini sesuai
fitur yang nanti dibuat. Batas HTTP 60 detik; tidak ada retry otomatis atau
fallback model. Responses API memakai `store: false`.

Verifikasi AI-01 memakai HTTP mock dan key dummy, bukan akun/provider live.
Tes memeriksa request, JSON hasil, schema mismatch, config precedence, key kosong,
refusal, incomplete, timeout, dan HTTP 400/401/429/500. Akses model/key akun aktual
belum diuji. Tidak ada perubahan UI, endpoint publik, atau deployment.

Referensi resmi:
- [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)
- [Structured Outputs / Responses API](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)
