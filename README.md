<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>
<h1>Neutrino Pipeline: Sterile Neutrino Cosmology Automation</h1>
<p>This repository provides a fully automated Python pipeline for scanning over sterile neutrino masses and mixing angles, running production and cosmological calculations, and analyzing their cosmological impact through power spectrum fitting.</p>
<p>It integrates:</p>
<ul>
  <li><strong><a href="https://urldefense.com/v3/__https://github.com/ntveem/sterile-dm__;!!CzAuKJ42GuquVTTmVmPViYEvSg!Pw4sUtYNWZRpininvG_bbd21bDR_Px9WxoXbTLYAeoZCvcdYtClDnLw2FnnrPIbxDztKo3tSnPepG3I$">sterile-dm</a></strong> (Fortran code for out-of-equilibrium sterile neutrino production)</li>
  <li><strong><a href="https://urldefense.com/v3/__https://github.com/lesgourg/class_public__;!!CzAuKJ42GuquVTTmVmPViYEvSg!Pw4sUtYNWZRpininvG_bbd21bDR_Px9WxoXbTLYAeoZCvcdYtClDnLw2FnnrPIbxDztKo3tSt9ml2RI$">CLASS</a></strong> (Boltzmann code for computing cosmological power spectra)</li>
</ul>
<p>The pipeline handles input generation, execution of external codes, postprocessing, and visualization for a complete sterile neutrino cosmology study.</p>


<hr>

<h2>⚙️ Requirements</h2>

<h3>✅ Software</h3>
<p>You need to <strong>install and compile</strong> the following separately:</p>

<ol>
  <li><a href="https://urldefense.com/v3/__https://github.com/ntveem/sterile-dm__;!!CzAuKJ42GuquVTTmVmPViYEvSg!Pw4sUtYNWZRpininvG_bbd21bDR_Px9WxoXbTLYAeoZCvcdYtClDnLw2FnnrPIbxDztKo3tSnPepG3I$">sterile-dm</a>
    <ul>
      <li>Clone and compile using a Fortran compiler</li>
      <li><strong>Important:</strong> Best compiled using an older compiler (e.g., <code>gfortran 4.9.2</code>) — newer versions may require patching</li>
      <li>Follow instructions in <code>sterile-nu</code> ReadMe</li>
      <li>Make sure the executable  <code>sterile-nu</code> is generated and test using the default params.ini file</li>
      <li>You may find it helpful to use <a href="https://urldefense.com/v3/__https://ftp.gnu.org/gnu/gcc/__;!!CzAuKJ42GuquVTTmVmPViYEvSg!Pw4sUtYNWZRpininvG_bbd21bDR_Px9WxoXbTLYAeoZCvcdYtClDnLw2FnnrPIbxDztKo3tSqj8Yg3M$">https://ftp.gnu.org/gnu/gcc/</a> to access old Fortran, then in the sterile-dm directory, run ./configure, before pasting 
        with the following changes to the Makefile: FC = "Path-to-old-gfortran" and FFLAGS =-L/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib 
      </li>
      <li>Some testing shows that gcc 15 may be more compatible </li>
    </ul>
  </li>
  <li><a href="https://urldefense.com/v3/__https://github.com/lesgourg/class_public__;!!CzAuKJ42GuquVTTmVmPViYEvSg!Pw4sUtYNWZRpininvG_bbd21bDR_Px9WxoXbTLYAeoZCvcdYtClDnLw2FnnrPIbxDztKo3tSt9ml2RI$">CLASS</a>
    <ul>
      <li>Download and compile CLASS following ReadMe instructions</li>
      <li>Make sure the binary is named <code>class</code></li>
    </ul>
  </li>
</ol>

<h3>✅ Python</h3>
<p>You’ll need Python 3.8+ and the following packages:</p>
<pre><code>pip install numpy scipy matplotlib pandas</code></pre>

<hr>

<h2>📂 Directory Structure</h2>
<pre><code>neutrino_pipeline/
├── config.py                # Where you provide inputs
├── main.py                  # Runs the entire pipeline
├── runner.py                # Handles one (mass, angle) point
├── run_production.py        # Runs sterile-dm
├── prepare_class_input.py   # Modifies PSD, generates .ini
├── run_class.py             # Executes CLASS
├── postprocess.py           # Computes T(k), fits for thermal mass
├── utils.py                 # Utility functions (lepton #, summaries)
├── outputs/                 # Results saved here
│   └── m_X_theta_Y/         # Per-run directory
│       ├── sterile_dm/
│       ├── class_input/
│       ├── class_output/
│       ├── plots/
│       └── summary.html
</code></pre>

<hr>

<h2>🛠️ How It Works</h2>

<h3>1. <strong>Define Your Grid</strong></h3>
<p>Edit <code>config.py</code>:</p>
<pre><code>mass_grid = [0.01, 0.1, 1.0]      # in keV
theta_grid = [1e-8, 1e-6]         # sin^2(2theta)</code></pre>
<p>You can also use numpy arrays to define your grid. Also specify the locations of your external codes:</p>
<pre><code>sterile_dm_path = "/path/to/sterile-dm"
class_path = "/path/to/class"
lcdm_reference_path = "/path/to/LCDM.dat"  # Reference power spectrum (example provided)
</code></pre>

<h3>2. <strong>Run the Pipeline</strong></h3>
<p>From the top-level directory:</p>
<pre><code>python main.py</code></pre>

<p>This will launch multiple processes (using all CPU cores) and iterate over the full grid.</p>

<p>Each run performs:</p>
<ol>
  <li>Creates a custom <code>params.ini</code> and runs <strong>sterile-dm</strong></li>
  <li>Locates the resulting PSD file (depends on mass, mixing angle, and generated lepton asymmetry <code>L</code>)</li>
  <li>Downsamples and rescales the PSD</li>
  <li>Generates a complete <code>.ini</code> file for <strong>CLASS</strong></li>
  <li>Copies the modified PSD into the CLASS working directory</li>
  <li>Runs <strong>CLASS</strong>, producing <code>pk.dat</code></li>
  <li>Computes the transfer function T(k) relative to LCDM</li>
  <li>Fits T(k) to extract a thermal mass</li>
  <li>Saves all results and plots</li>
</ol>

<h3>3. <strong>Explore the Results</strong></h3>
<p>After finishing, browse the <code>outputs/</code> folder. Each run directory contains:</p>
<ul>
  <li><code>results.json</code>: Mass, mixing angle, lepton number, thermal mass</li>
  <li><code>summary.html</code>: Quick-look plots and parameter values</li>
  <li><code>class_output/</code>: CLASS logs and power spectra</li>
</ul>

<hr>

<h2>📈 Plots and Output</h2>
<p>Each grid point generates:</p>
<ul>
  <li>Modified phase space distribution plot (f*q**2 vs q</li>
  <li>Transfer function plot (T(k) with best-fit model)</li>
</ul>

<hr>

<h2>🔁 Restarting or Debugging</h2>
<ul>
  <li>Safe to rerun <code>python main.py</code> if interupted: it skips point processes that already finished</li>
  <li>If a run crashes, check <code>error.log</code> and <code>run.log</code> inside that point’s output directory</li>
  <li>You can safely delete any broken run subfolder and rerun</li>
</ul>

<hr>

<h2>✅ Best Practices</h2>
<ul>
  <li>Back up your <code>params.ini</code> inside <code>sterile-dm</code> (the pipeline will restore it after each run)</li>
  <li>Don’t manually edit output folders during execution</li>
  <li>Keep LCDM reference spectra consistent across all runs and ensure it matche your cosmology while extending to an adequate Pkmax</li>
</ul>

<hr>

<h2>🙋‍♀️ Questions?</h2>
<p>You can email <a href="mailto:garciaeh@uci.edu">garciaeh@uci.edu</a> or <a href="mailto:cvogel1@uci.edu">cvogel1@uci.edu</a> for assistance with this script.</p>

<hr>

<h2>📜 Citation</h2>
<p>If this pipeline contributes to your research, please consider citing our original paper.</p>
</body></html>
