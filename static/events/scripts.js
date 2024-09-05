document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('event-search');

    searchInput.addEventListener('input', function () {
        const query = searchInput.value;
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `?q=${encodeURIComponent(query)}`, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        
        xhr.onload = function () {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                
                const upcomingEventsContainer = document.getElementById('upcoming-events');
                const otherEventsContainer = document.getElementById('other-events');

                let upcomingEventsHTML = '';
                data.upcoming_events.forEach(function (event) {
                    upcomingEventsHTML += `
                        <div class="col-md-4 mb-4">
                            <div class="card event-card text-center">
                                ${event.poster_url ? `<img src="${event.poster_url}" class="card-img-top event-poster" alt="${event.title}">` : `<img src="/static/images/no-image.png" class="card-img-top event-poster" alt="No Image Available">`}
                                <div class="card-body">
                                    <h5 class="card-title fancy-font">${event.title}</h5>
                                    <p class="venue"><i class="bi bi-geo-alt-fill"></i> ${event.venue_name}</p>
                                    <p class="creator"><i class="bi bi-person-fill"></i> Created by ${event.vendor_name} from ${event.vendor_store}</p>
                                    <a href="${event.event_url}" class="btn btn-outline-danger">Get Tickets</a>
                                </div>
                            </div>
                        </div>`;
                });
                
                let otherEventsHTML = '';
                data.other_events.forEach(function (event) {
                    otherEventsHTML += `
                        <div class="col-md-4 mb-4">
                            <div class="card event-card text-center">
                                ${event.poster_url ? `<img src="${event.poster_url}" class="card-img-top event-poster" alt="${event.title}">` : `<img src="/static/images/no-image.png" class="card-img-top event-poster" alt="No Image Available">`}
                                <div class="card-body">
                                    <h5 class="card-title fancy-font">${event.title}</h5>
                                    <p class="venue"><i class="bi bi-geo-alt-fill"></i> ${event.venue_name}</p>
                                    <p class="creator"><i class="bi bi-person-fill"></i> Created by ${event.vendor_name} from ${event.vendor_store}</p>
                                    <a href="${event.event_url}" class="btn btn-outline-danger">Get Tickets</a>
                                </div>
                            </div>
                        </div>`;
                });

                upcomingEventsContainer.innerHTML = upcomingEventsHTML;
                otherEventsContainer.innerHTML = otherEventsHTML;
            }
        };

        xhr.send();
    });
});
