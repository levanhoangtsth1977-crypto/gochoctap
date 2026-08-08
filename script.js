"use strict";

document.addEventListener("DOMContentLoaded", function() {
    console.log("🚀 Góc Học Tập Thầy Lê Văn Hoàng - Hệ thống điều hướng đã sẵn sàng!");
    initGiaoAnModule();
    initPhieuHocTapModule();
    initDeKiemTraModule();
    initGlobalFileUpload();
});

// Bộ lưu trữ dữ liệu tệp tải lên từ máy tính theo Tuần/Mốc và Môn học
const globalUploadedStore = {
    giaoAn: {},
    phieuHocTap: {},
    deKiemTra: {}
};

// --- MODULE 1: GIÁO ÁN & KẾ HOẠCH ---
function initGiaoAnModule() {
    const selectTuan = document.getElementById("tuanChungSelect");
    const hienThiTuanText = document.getElementById("hienThiTuanText");
    if (!selectTuan) return;

    if (selectTuan.children.length === 0) {
        const fragment = document.createDocumentFragment();
        for (let i = 1; i <= 35; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = `Tuần ${i}`;
            fragment.appendChild(option);
        }
        selectTuan.appendChild(fragment);
    }

    function capNhatLienKetGiaoAn(tuan) {
        if (hienThiTuanText) {
            hienThiTuanText.textContent = `ĐANG XEM: TUẦN ${tuan} | Hệ thống tự động nhận diện học liệu theo tuần`;
        }
        
        const cards = document.querySelectorAll(".card[data-mon]");
        cards.forEach(card => {
            const mon = card.getAttribute("data-mon");
            const btnView = card.querySelector(".btn-view-main, .btn-view");
            const btnDownload = card.querySelector(".btn-download, .btn-word");
            const statusIndicator = card.querySelector(".file-status-indicator");

            // Kiểm tra xem tuần này đã có tệp tải lên từ máy tính chưa
            if (globalUploadedStore.giaoAn[tuan] && globalUploadedStore.giaoAn[tuan][mon]) {
                const fileData = globalUploadedStore.giaoAn[tuan][mon];
                if (btnView) btnView.href = fileData.url;
                if (btnDownload) {
                    btnDownload.href = fileData.url;
                    btnDownload.download = fileData.name;
                }
                if (statusIndicator) {
                    statusIndicator.textContent = `✅ Đã tải lên [Tuần ${tuan}]: ${fileData.name}`;
                    statusIndicator.style.display = "block";
                }
            } else {
                let pdfPath = mon === "ke-hoach-day-hoc" ? `tai-lieu/ke-hoach-day-hoc/ke-hoach-tuan-${tuan}.pdf` :
                              mon === "giao-an-tong-hop" ? `tai-lieu/giao-an-tong-hop/giao-an-tong-hop-tuan-${tuan}.pdf` :
                              `tai-lieu/${mon}/${mon}-tuan-${tuan}.pdf`;
                              
                let wordPath = mon === "ke-hoach-day-hoc" ? `tai-lieu/ke-hoach-day-hoc/ke-hoach-tuan-${tuan}.docx` :
                               mon === "giao-an-tong-hop" ? `tai-lieu/giao-an-tong-hop/giao-an-tong-hop-tuan-${tuan}.docx` :
                               `tai-lieu/${mon}/${mon}-tuan-${tuan}.docx`;

                if (btnView) {
                    btnView.href = pdfPath;
                    btnView.setAttribute("target", "_blank");
                }
                if (btnDownload) {
                    btnDownload.href = wordPath;
                    btnDownload.removeAttribute("download");
                }
                if (statusIndicator) statusIndicator.style.display = "none";
            }
        });
    }

    capNhatLienKetGiaoAn(selectTuan.value || 1);
    selectTuan.addEventListener("change", function() {
        capNhatLienKetGiaoAn(this.value);
    });
}

// --- MODULE 2: PHIẾU HỌC TẬP ---
function initPhieuHocTapModule() {
    const selectTuanPhieu = document.getElementById("tuanChungPhieuSelect");
    const hienThiTuanPhieuText = document.getElementById("hienThiTuanPhieuText");
    if (!selectTuanPhieu) return;

    if (selectTuanPhieu.children.length === 0) {
        const fragment = document.createDocumentFragment();
        for (let i = 1; i <= 35; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = `Tuần ${i}`;
            fragment.appendChild(option);
        }
        selectTuanPhieu.appendChild(fragment);
    }

    function capNhatPhieuHocTap(tuan) {
        if (hienThiTuanPhieuText) {
            hienThiTuanPhieuText.textContent = `ĐANG XEM: TUẦN ${tuan}`;
        }

        const cards = document.querySelectorAll(".card[data-phieu-mon]");
        cards.forEach(card => {
            const mon = card.getAttribute("data-phieu-mon");
            const btnView = card.querySelector(".btn-view-main, .btn-view");
            const btnDownload = card.querySelector(".btn-download, .btn-word");
            const statusIndicator = card.querySelector(".file-status-indicator");

            if (globalUploadedStore.phieuHocTap[tuan] && globalUploadedStore.phieuHocTap[tuan][mon]) {
                const fileData = globalUploadedStore.phieuHocTap[tuan][mon];
                if (btnView) btnView.href = fileData.url;
                if (btnDownload) {
                    btnDownload.href = fileData.url;
                    btnDownload.download = fileData.name;
                }
                if (statusIndicator) {
                    statusIndicator.textContent = `✅ Đã tải lên [Tuần ${tuan}]: ${fileData.name}`;
                    statusIndicator.style.display = "block";
                }
            } else {
                let path = `tai-lieu/phieu-hoc-tap/${mon}/${mon}-tuan-${tuan}`;
                if (btnView) btnView.href = `${path}.pdf`;
                if (btnDownload) {
                    btnDownload.href = `${path}.docx`;
                    btnDownload.removeAttribute("download");
                }
                if (statusIndicator) statusIndicator.style.display = "none";
            }
        });
    }

    capNhatPhieuHocTap(selectTuanPhieu.value || 1);
    selectTuanPhieu.addEventListener("change", function() {
        capNhatPhieuHocTap(this.value);
    });
}

// --- MODULE 3: ĐỀ KIỂM TRA ĐỊNH KỲ ---
function initDeKiemTraModule() {
    const selectMocKT = document.getElementById("mocKiemTraSelect");
    const hienThiMocText = document.getElementById("hienThiMocText");
    if (!selectMocKT) return;

    function capNhatDeKiemTra() {
        const moc = selectMocKT.value || "cuoi-ky-2";
        const text = selectMocKT.options[selectMocKT.selectedIndex] ? selectMocKT.options[selectMocKT.selectedIndex].text : "CUỐI HỌC KỲ 2";
        
        if (hienThiMocText) {
            hienThiMocText.textContent = `ĐANG XEM: ${text.toUpperCase()} | Năm học 2026–2027`;
        }

        const cards = document.querySelectorAll(".card[data-de-mon]");
        cards.forEach(card => {
            const mon = card.getAttribute("data-de-mon");
            const btnView = card.querySelector(".btn-view-main, .btn-view");
            const btnDownload = card.querySelector(".btn-download, .btn-word");
            const statusIndicator = card.querySelector(".file-status-indicator");

            if (globalUploadedStore.deKiemTra[moc] && globalUploadedStore.deKiemTra[moc][mon]) {
                const fileData = globalUploadedStore.deKiemTra[moc][mon];
                if (btnView) btnView.href = fileData.url;
                if (btnDownload) {
                    btnDownload.href = fileData.url;
                    btnDownload.download = fileData.name;
                }
                if (statusIndicator) {
                    statusIndicator.textContent = `✅ Đã tải lên [${text}]: ${fileData.name}`;
                    statusIndicator.style.display = "block";
                }
            } else {
                let path = `tai-lieu/de-kiem-tra/${mon}/${moc}`;
                if (btnView) {
                    btnView.href = `${path}.pdf`;
                    btnView.setAttribute("target", "_blank");
                }
                if (btnDownload) {
                    btnDownload.href = `${path}.docx`;
                    btnDownload.removeAttribute("download");
                }
                if (statusIndicator) statusIndicator.style.display = "none";
            }
        });
    }

    capNhatDeKiemTra();
    selectMocKT.addEventListener("change", capNhatDeKiemTra);
}

// --- HỖ TRỢ XỬ LÝ TẢI FILE TỪ MÁY TÍNH DÙNG CHUNG ---
function initGlobalFileUpload() {
    window.xuLyLuuFileMayTinh = function(moduleType, currentKey, monKey, file) {
        if (!file) return;
        const fileUrl = URL.createObjectURL(file);
        
        if (!globalUploadedStore[moduleType][currentKey]) {
            globalUploadedStore[moduleType][currentKey] = {};
        }
        globalUploadedStore[moduleType][currentKey][monKey] = {
            name: file.name,
            url: fileUrl
        };
    };
}