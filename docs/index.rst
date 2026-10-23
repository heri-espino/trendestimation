trendestimation
===============

.. raw:: html

   <div class="te-landing">
     <section class="te-hero" aria-labelledby="te-hero-title">
       <div class="te-hero-copy">
         <div class="te-eyebrow"><span class="te-status-dot" aria-hidden="true"></span> Scientific Python <span class="te-eyebrow-divider" aria-hidden="true"></span> Pre-release 0.1</div>
         <h2 id="te-hero-title">Finite-difference<br><span>trend estimation.</span></h2>
         <p class="te-hero-description">Penalized least-squares smoothing for equally spaced time series. Choose a difference order, select a penalty, and examine the fitted trend through documented Python methods and executable notebooks.</p>
         <div class="te-actions">
           <a class="te-button te-button-primary" href="notebooks.html">Explore notebooks <span aria-hidden="true">&rarr;</span></a>
           <a class="te-button te-button-secondary" href="api.html">Explore the API <span aria-hidden="true">&nearr;</span></a>
         </div>
         <p class="te-hero-footnote">In-sample estimation &middot; Explicit assumptions &middot; Reproducible examples</p>
       </div>
       <div class="te-hero-visual">
         <div class="te-chart-panel">
           <div class="te-chart-top"><span class="te-chart-kicker">SIGNAL / TREND</span><span class="te-chart-dots" aria-hidden="true"><i></i><i></i><i></i></span></div>
           <svg class="te-chart" viewBox="0 0 520 290" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="te-chart-title te-chart-desc">
             <title id="te-chart-title">Illustrative trend smoothing</title>
             <desc id="te-chart-desc">A jagged observed series and a smoother estimated trend both increase over time. The curves are decorative synthetic data, not a benchmark or statistical result.</desc>
             <g class="te-grid">
               <path d="M30 38H492 M30 94H492 M30 150H492 M30 206H492 M30 262H492" />
               <path d="M30 20V262 M122 20V262 M214 20V262 M306 20V262 M398 20V262 M492 20V262" />
             </g>
             <path class="te-observed" d="M30 236 L48 212 L65 221 L84 193 L101 233 L118 176 L138 189 L155 182 L174 206 L191 159 L212 178 L230 172 L251 203 L270 133 L287 150 L307 107 L325 145 L343 122 L361 111 L379 145 L397 94 L414 104 L433 70 L451 94 L472 83 L492 58" />
             <path class="te-trend-glow" d="M30 225 C80 218 108 196 155 185 S233 176 270 145 S352 116 390 107 S449 84 492 70" />
             <path class="te-trend" d="M30 225 C80 218 108 196 155 185 S233 176 270 145 S352 116 390 107 S449 84 492 70" />
             <circle class="te-endpoint" cx="492" cy="70" r="5" />
           </svg>
           <div class="te-chart-legend"><span><i class="te-legend-observed"></i> Observations</span><span><i class="te-legend-trend"></i> Estimated trend</span></div>
         </div>
         <p class="te-illustration-caption">Illustrative synthetic series &middot; Not an empirical result</p>
       </div>
     </section>

     <section class="te-section" aria-labelledby="te-capabilities-heading">
       <div class="te-section-heading">
         <div><p class="te-overline">THE TOOLKIT</p><h2 id="te-capabilities-heading">Methods and documentation</h2></div>
         <p>Implementation details, parameter selection, and the <a href="handbook/index.html">mathematical handbook</a>.</p>
       </div>
       <div class="te-feature-grid">
         <a class="te-feature" href="mathematics.html">
           <span class="te-feature-number">01 / ESTIMATION</span>
           <span class="te-feature-icon" aria-hidden="true">&#8767;</span>
           <h3>Penalized least squares</h3>
           <p>Estimate smooth trends using finite differences of any admissible integer order, with fixed or observed-difference reference means.</p>
           <span class="te-feature-link">Read the mathematics <span aria-hidden="true">&rarr;</span></span>
         </a>
         <a class="te-feature" href="smoothness_optimization.html">
           <span class="te-feature-number">02 / SELECTION</span>
           <span class="te-feature-icon" aria-hidden="true">&#955;</span>
           <h3>Choose the smoothing</h3>
           <p>Compare CV, GCV, AICc, BIC, and Gaussian marginal MLE; alternatively specify a target smoothness.</p>
           <span class="te-feature-link">Read optimization guide <span aria-hidden="true">&rarr;</span></span>
         </a>
         <a class="te-feature" href="benchmarks.html">
           <span class="te-feature-number">03 / COMPUTATION</span>
           <span class="te-feature-icon" aria-hidden="true">&#931;</span>
           <h3>Reusable spectral solver</h3>
           <p>Reuse a spectral decomposition across smoothing parameters; inspect effective degrees of freedom and the exact limiting trend.</p>
           <span class="te-feature-link">Why it is fast <span aria-hidden="true">&rarr;</span></span>
         </a>
       </div>
     </section>

     <section class="te-demo" aria-labelledby="te-demo-heading">
       <div class="te-demo-copy">
         <p class="te-overline">START WITH PYTHON</p>
         <h2 id="te-demo-heading">A concise Python workflow</h2>
         <p>Construct a smoother, select the penalty with GCV, and obtain a fitted trend from a seeded synthetic series.</p>
         <a class="te-text-link" href="notebooks.html">Explore the Jupyter notebooks <span aria-hidden="true">&rarr;</span></a>
       </div>
       <div class="te-code-window">
         <div class="te-code-header"><span class="te-code-dots" aria-hidden="true"><i></i><i></i><i></i></span><span>example.py</span><span>PYTHON</span></div>
         <pre class="te-code"><code><span class="te-code-keyword">import</span> numpy <span class="te-code-keyword">as</span> np
   <span class="te-code-keyword">from</span> trendestimation <span class="te-code-keyword">import</span> TrendSmoother, select_lambda

   rng = np.random.default_rng(<span class="te-code-number">7</span>)
   t = np.arange(<span class="te-code-number">120</span>)
   y = np.sin(t / <span class="te-code-number">14</span>) + rng.normal(<span class="te-code-number">0</span>, <span class="te-code-number">.25</span>, len(t))

   solver = TrendSmoother(len(y), order=<span class="te-code-number">2</span>)
   best = select_lambda(solver, y, criterion=<span class="te-code-string">"gcv"</span>)
   trend = solver.fit(y, lambda_=best.lambda_).trend</code></pre>
       </div>
     </section>

     <section class="te-footer-panel" aria-labelledby="te-scope-heading">
       <div><p class="te-overline">SCIENTIFIC SCOPE</p><h2 id="te-scope-heading">Scope and assumptions</h2><p>The current package implements published in-sample smoothing methods. It does not claim forecast-optimal tuning, rolling time-series cross-validation, or new forecasting estimators.</p></div>
       <a class="te-button te-button-outline" href="mathematics.html">Methods and assumptions <span aria-hidden="true">&rarr;</span></a>
     </section>
   </div>

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Documentation

   quickstart
   forecasting
   notebooks
   gallery
   mathematics
   smoothness_optimization
   handbook/index
   benchmarks
   references
   api

