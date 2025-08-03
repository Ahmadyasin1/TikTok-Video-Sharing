// Main JavaScript for Video Sharing Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Video thumbnail hover effects
    const videoThumbnails = document.querySelectorAll('.video-thumbnail');
    videoThumbnails.forEach(function(thumbnail) {
        if (thumbnail.tagName === 'VIDEO') {
            thumbnail.addEventListener('mouseenter', function() {
                this.play();
            });
            
            thumbnail.addEventListener('mouseleave', function() {
                this.pause();
                this.currentTime = 0;
            });
        }
    });

    // Search form enhancements
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[type="search"]');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(function() {
                    // Auto-submit search after 500ms of no typing
                    if (searchInput.value.length > 2) {
                        searchForm.submit();
                    }
                }, 500);
            });
        }
    }

    // File upload validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                // Check file size (50MB limit)
                const maxSize = 50 * 1024 * 1024; // 50MB in bytes
                if (file.size > maxSize) {
                    alert('File size too large. Maximum size is 50MB.');
                    this.value = '';
                    return;
                }

                // Check file type for video uploads
                if (this.accept && this.accept.includes('video/*')) {
                    const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo'];
                    if (!allowedTypes.includes(file.type)) {
                        alert('Invalid file type. Please upload MP4, AVI, or MOV files.');
                        this.value = '';
                        return;
                    }
                }

                // Show file info
                const fileName = file.name;
                const fileSize = (file.size / (1024 * 1024)).toFixed(2);
                console.log(`Selected file: ${fileName} (${fileSize} MB)`);
            }
        });
    });

    // Lazy loading for video thumbnails
    const lazyVideos = document.querySelectorAll('video[data-src]');
    const videoObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const video = entry.target;
                video.src = video.dataset.src;
                video.load();
                videoObserver.unobserve(video);
            }
        });
    });

    lazyVideos.forEach(function(video) {
        videoObserver.observe(video);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Infinite scroll for video grid (optional enhancement)
    let page = 1;
    let loading = false;
    
    function loadMoreVideos() {
        if (loading) return;
        loading = true;
        
        // Show loading indicator
        const loader = document.querySelector('.loading-indicator');
        if (loader) {
            loader.style.display = 'block';
        }
        
        // Simulate API call (replace with actual implementation)
        setTimeout(function() {
            loading = false;
            if (loader) {
                loader.style.display = 'none';
            }
            page++;
        }, 1000);
    }

    // Check if we're on the dashboard page
    if (window.location.pathname === '/' || window.location.pathname.includes('dashboard')) {
        window.addEventListener('scroll', function() {
            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1000) {
                loadMoreVideos();
            }
        });
    }
});

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(function() {
        toast.remove();
    }, 3000);
}

// AJAX helper function
function makeAjaxRequest(url, method, data, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    callback(null, response);
                } catch (e) {
                    callback(e, null);
                }
            } else {
                callback(new Error('Request failed'), null);
            }
        }
    };
    
    xhr.send(data);
}

// Video player enhancements
function initializeVideoPlayer(videoElement) {
    if (!videoElement) return;
    
    // Add custom controls
    videoElement.addEventListener('loadedmetadata', function() {
        console.log('Video duration:', this.duration);
    });
    
    videoElement.addEventListener('timeupdate', function() {
        // Update progress bar if custom controls are implemented
    });
    
    // Keyboard shortcuts
    videoElement.addEventListener('keydown', function(e) {
        switch(e.key) {
            case ' ':
                e.preventDefault();
                if (this.paused) {
                    this.play();
                } else {
                    this.pause();
                }
                break;
            case 'ArrowLeft':
                this.currentTime -= 10;
                break;
            case 'ArrowRight':
                this.currentTime += 10;
                break;
            case 'ArrowUp':
                this.volume = Math.min(1, this.volume + 0.1);
                break;
            case 'ArrowDown':
                this.volume = Math.max(0, this.volume - 0.1);
                break;
        }
    });
}

// Initialize video players on page load
document.addEventListener('DOMContentLoaded', function() {
    const videos = document.querySelectorAll('video');
    videos.forEach(initializeVideoPlayer);
});
