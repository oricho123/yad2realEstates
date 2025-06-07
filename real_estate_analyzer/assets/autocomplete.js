window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    initAutocomplete: function (id) {
      const container = document.getElementById("autocomplete-container");
      if (document.getElementById("autocomplete-input")) return "";

      // Create input
      const input = document.createElement("input");
      input.setAttribute("id", "autocomplete-input");
      input.setAttribute(
        "placeholder",
        "Type city or area name (minimum 2 letters)..."
      );
      input.style.cssText = `
                width: 100%;
                padding: 12px;
                border-radius: 8px;
                border: 2px solid #e9ecef;
                font-size: 14px;
                outline: none;
                transition: border-color 0.3s ease;
            `;
      container?.appendChild(input);

      // Create results container
      const resultsContainer = document.createElement("div");
      resultsContainer.setAttribute("id", "autocomplete-results");
      resultsContainer.style.cssText = `
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #e9ecef;
                border-top: none;
                border-radius: 0 0 8px 8px;
                max-height: 300px;
                overflow-y: auto;
                z-index: 1000;
                display: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            `;
      container?.appendChild(resultsContainer);

      // Style the container for proper positioning
      if (container) {
        container.style.position = "relative";
      }

      let debounceTimeout;
      let selectedData = null;

      // Input event handler
      input.addEventListener("input", function (e) {
        const query = e?.target?.value?.trim();

        if (query.length < 2) {
          resultsContainer.style.display = "none";
          return;
        }

        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(async () => {
          try {
            const response = await fetch(
              `/proxy_yad2_autocomplete?text=${encodeURIComponent(query)}`
            );
            const data = await response.json();

            displayResults(data);
          } catch (error) {
            console.error("Error fetching autocomplete data:", error);
            resultsContainer.style.display = "none";
          }
        }, 300);
      });

      // Function to display results
      function displayResults(data) {
        resultsContainer.innerHTML = "";

        const hasResults =
          (data.cities && data.cities.length > 0) ||
          (data.areas && data.areas.length > 0) ||
          (data.hoods && data.hoods.length > 0);

        if (!hasResults) {
          resultsContainer.style.display = "none";
          return;
        }

        // Add cities
        if (data.cities && data.cities.length > 0) {
          const citiesHeader = document.createElement("div");
          citiesHeader.textContent = "Cities";
          citiesHeader.style.cssText = `
                        padding: 8px 12px;
                        background: #f8f9fa;
                        font-weight: bold;
                        color: #495057;
                        border-bottom: 1px solid #e9ecef;
                    `;
          resultsContainer.appendChild(citiesHeader);

          data.cities.forEach((city) => {
            const item = createResultItem(city.fullTitleText, {
              type: "city",
              cityId: city.cityId,
              areaId: city.areaId,
              topAreaId: city.topAreaId,
              fullText: city.fullTitleText,
            });
            resultsContainer.appendChild(item);
          });
        }

        // Add areas
        if (data.areas && data.areas.length > 0) {
          const areasHeader = document.createElement("div");
          areasHeader.textContent = "Areas";
          areasHeader.style.cssText = `
                        padding: 8px 12px;
                        background: #f8f9fa;
                        font-weight: bold;
                        color: #495057;
                        border-bottom: 1px solid #e9ecef;
                    `;
          resultsContainer.appendChild(areasHeader);

          data.areas.forEach((area) => {
            const item = createResultItem(area.fullTitleText, {
              type: "area",
              areaId: area.areaId,
              topAreaId: area.topAreaId,
              fullText: area.fullTitleText,
            });
            resultsContainer.appendChild(item);
          });
        }

        // Add neighborhoods/hoods
        if (data.hoods && data.hoods.length > 0) {
          const hoodsHeader = document.createElement("div");
          hoodsHeader.textContent = "Neighborhoods";
          hoodsHeader.style.cssText = `
                        padding: 8px 12px;
                        background: #f8f9fa;
                        font-weight: bold;
                        color: #495057;
                        border-bottom: 1px solid #e9ecef;
                    `;
          resultsContainer.appendChild(hoodsHeader);

          data.hoods.forEach((hood) => {
            const item = createResultItem(hood.fullTitleText, {
              type: "hood",
              cityId: hood.cityId,
              hoodId: hood.hoodId,
              areaId: hood.areaId,
              topAreaId: hood.topAreaId,
              fullText: hood.fullTitleText,
            });
            resultsContainer.appendChild(item);
          });
        }

        resultsContainer.style.display = "block";
      }

      // Function to create result item
      function createResultItem(text, data) {
        const item = document.createElement("div");
        item.textContent = text;
        item.style.cssText = `
                    padding: 10px 12px;
                    cursor: pointer;
                    border-bottom: 1px solid #f1f3f4;
                    transition: background-color 0.2s ease;
                `;

        item.addEventListener("mouseenter", function () {
          item.style.backgroundColor = "#f8f9fa";
        });

        item.addEventListener("mouseleave", function () {
          item.style.backgroundColor = "white";
        });

        item.addEventListener("click", function () {
          input.value = text;
          selectedData = data;
          resultsContainer.style.display = "none";

          // Store selected value in Dash Store
          if (window.dash_clientside) {
            // Create a custom event to trigger Dash callback
            const event = new CustomEvent("autocomplete-selection", {
              detail: data,
            });
            input.dispatchEvent(event);
          }
        });

        return item;
      }

      // Hide results when clicking outside
      document.addEventListener("click", function (e) {
        if (!container?.contains(e.target)) {
          resultsContainer.style.display = "none";
        }
      });

      // Focus styling
      input.addEventListener("focus", function () {
        input.style.borderColor = "#007bff";
      });

      input.addEventListener("blur", function () {
        // Delay hiding to allow for click events
        setTimeout(() => {
          if (!container?.contains(document.activeElement)) {
            input.style.borderColor = "#e9ecef";
            resultsContainer.style.display = "none";
          }
        }, 150);
      });

      return "";
    },
  },
});
