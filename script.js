// =========================================================
// MÃ XỬ LÝ CHUẨN: XEM (PDF), TẢI VỀ (WORD) VÀ TẢI LÊN (GOOGLE FORM)
// =========================================================

// Đường dẫn Google Form nhận tệp của ông chủ
const LINK_GOOGLE_FORM = "https://forms.gle/qB8zSjDDzYCNx3uU7"; 

document.addEventListener('DOMContentLoaded', function () {
    const selectTuan = document.getElementById('select-tuan');
    
    if (selectTuan) {
        capNhatToanBoLienKet(selectTuan.value || 1);

        selectTuan.addEventListener('change', function () {
            const tuanSo = this.value.toString().replace(/[^0-9]/g, '') || 1;
            capNhatToanBoLienKet(tuanSo);
        });
    }
});

function capNhatToanBoLienKet(tuanSo) {
    const dsMon = [
        { idXem: 'btn-xem-kehoach', idTai: 'btn-tai-kehoach', idUp: 'btn-up-kehoach', folder: 'ke-hoach-day-hoc', prefix: 'ke-hoach-tuan' },
        { idXem: 'btn-xem-giaoan', idTai: 'btn-tai-giaoan', idUp: 'btn-up-giaoan', folder: 'giao-an', prefix: 'giao-an-tuan' },
        { idXem: 'btn-xem-tiengviet', idTai: 'btn-tai-tiengviet', idUp: 'btn-up-tiengviet', folder: 'giao-an', prefix: 'tieng-viet-tuan' },
        { idXem: 'btn-xem-toan', idTai: 'btn-tai-toan', idUp: 'btn-up-toan', folder: 'giao-an', prefix: 'toan-tuan' },
        { idXem: 'btn-xem-khoahoc', idTai: 'btn-tai-khoahoc', idUp: 'btn-up-khoahoc', folder: 'giao-an', prefix: 'khoa-hoc-tuan' },
        { idXem: 'btn-xem-lsdl', idTai: 'btn-tai-lsdl', idUp: 'btn-up-lsdl', folder: 'giao-an', prefix: 'lich-su-dia-li-tuan' },
        { idXem: 'btn-xem-daoduc', idTai: 'btn-tai-daoduc', idUp: 'btn-up-daoduc', folder: 'giao-an', prefix: 'dao-duc-tuan' },
        { idXem: 'btn-xem-congnghe', idTai: 'btn-tai-congnghe', idUp: 'btn-up-congnghe', folder: 'giao-an', prefix: 'cong-nghe-tuan' },
        { idXem: 'btn-xem-hdtn', idTai: 'btn-tai-hdtn', idUp: 'btn-up-hdtn', folder: 'giao-an', prefix: 'hoat-dong-trai-nghiem-tuan' }
    ];

    dsMon.forEach(mon => {
        const duongDanPdf = `tai-lieu/${mon.folder}/${mon.prefix}-${tuanSo}.pdf`;
        const duongDanDocx = `tai-lieu/${mon.folder}/${mon.prefix}-${tuanSo}.docx`;

        const btnXem = document.getElementById(mon.idXem);
        const btnTai = document.getElementById(mon.idTai);
        const btnUp = document.getElementById(mon.idUp);

        if (btnXem) { btnXem.href = duongDanPdf; btnXem.target = "_blank"; }
        if (btnTai) { btnTai.href = duongDanDocx; btnTai.setAttribute('download', `${mon.prefix}-${tuanSo}.docx`); }
        if (btnUp) { btnUp.href = LINK_GOOGLE_FORM; btnUp.target = "_blank"; }
    });

    const txtThongBao = document.getElementById('txt-tuan-hien-tai');
    if (txtThongBao) {
        txtThongBao.innerText = `📖 ĐANG HIỂN THỊ HỌC LIỆU: TUẦN ${tuanSo} | Năm học 2026–2027`;
    }
}