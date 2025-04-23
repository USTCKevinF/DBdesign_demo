document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const createLogBtn = document.getElementById('createLogBtn');
    const logModal = document.getElementById('logModal');
    const closeBtn = document.querySelector('.close');
    const logForm = document.getElementById('logForm');
    const logsList = document.getElementById('logsList');

    // 加载日志列表
    loadLogs();

    // 新建日志按钮点击事件
    createLogBtn.addEventListener('click', function() {
        document.getElementById('modalTitle').textContent = '新建日志';
        document.getElementById('logId').value = '';
        document.getElementById('title').value = '';
        document.getElementById('content').value = '';
        logModal.style.display = 'block';
    });

    // 关闭模态框
    closeBtn.addEventListener('click', function() {
        logModal.style.display = 'none';
    });

    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target === logModal) {
            logModal.style.display = 'none';
        }
    });

    // 表单提交事件
    logForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const logId = document.getElementById('logId').value;
        const title = document.getElementById('title').value;
        const content = document.getElementById('content').value;

        if (logId) {
            updateLog(logId, title, content);
        } else {
            createLog(title, content);
        }
    });

    // 加载日志列表
    function loadLogs() {
        fetch('/api/logs')
            .then(response => response.json())
            .then(logs => {
                logsList.innerHTML = '';
                logs.forEach(log => {
                    const logItem = document.createElement('div');
                    logItem.className = 'log-item';
                    logItem.innerHTML = `
                        <h3>${log.title}</h3>
                        <p>${log.content}</p>
                        <p class="log-date">创建时间：${new Date(log.created_at).toLocaleString()}</p>
                        <div class="log-actions">
                            <button class="btn edit-btn" onclick="editLog(${log.log_id})">编辑</button>
                            <button class="btn delete-btn" onclick="deleteLog(${log.log_id})">删除</button>
                        </div>
                    `;
                    logsList.appendChild(logItem);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    // 创建日志
    function createLog(title, content) {
        fetch('/api/logs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content })
        })
        .then(response => response.json())
        .then(() => {
            logModal.style.display = 'none';
            loadLogs();
        })
        .catch(error => console.error('Error:', error));
    }

    // 更新日志
    function updateLog(logId, title, content) {
        fetch(`/api/logs/${logId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, content })
        })
        .then(response => response.json())
        .then(() => {
            logModal.style.display = 'none';
            loadLogs();
        })
        .catch(error => console.error('Error:', error));
    }

    // 删除日志
    window.deleteLog = function(logId) {
        if (confirm('确定要删除这条日志吗？')) {
            fetch(`/api/logs/${logId}`, {
                method: 'DELETE'
            })
            .then(() => loadLogs())
            .catch(error => console.error('Error:', error));
        }
    };

    // 编辑日志
    window.editLog = function(logId) {
        fetch(`/api/logs/${logId}`)
            .then(response => response.json())
            .then(log => {
                document.getElementById('modalTitle').textContent = '编辑日志';
                document.getElementById('logId').value = log.log_id;
                document.getElementById('title').value = log.title;
                document.getElementById('content').value = log.content;
                logModal.style.display = 'block';
            })
            .catch(error => console.error('Error:', error));
    };
}); 