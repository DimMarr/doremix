export function CguPage(container: HTMLElement) {
  const content = (
    <div class="max-w-4xl mx-auto py-12 px-6">
      <h1 class="text-3xl font-bold mb-8 text-white">Terms of Service</h1>

      <div class="space-y-8 text-neutral-300">

        <section class="bg-blue-900/20 border border-blue-500/30 p-6 rounded-lg mb-8">
          <h2 class="text-xl font-semibold text-blue-400 mb-3">Academic Project Disclaimer</h2>
          <p class="leading-relaxed">
            Dorémix is a strictly educational and non-profit project. It was developed by a team of 8 engineering students in their 3rd year of the DO (<i>Développement informatique et exploitation Opérationnelle</i>) major at Polytech Montpellier. This platform is hosted exclusively for academic evaluation and demonstration; it is not a commercial product.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">1. Service Overview</h2>
          <p class="leading-relaxed">
            Dorémix is an online music streaming platform. The purpose of these Terms of Service is to control how our services are accessed and used. You unconditionally accept these terms by using Dorémix.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">2. Service Access and Account</h2>
          <p class="leading-relaxed">
            To fully utilise Dorémix, a user account must be created. Since this is an academic project, any personal information gathered—like usernames or emails—is only used to show off the technical features of the application. It is your responsibility to keep your login information private.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">3. Intellectual Property</h2>
          <p class="leading-relaxed">
            The student team owns the intellectual property of Dorémix, including its original interfaces, architecture, and source code. However, under the educational exceptions to copyright law, any third-party content (music, album covers, audio samples) hosted on the platform is only used for instructional and illustrative purposes. The use of these works does not bring in any money for Dorémix.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">4. User Obligations</h2>
          <p class="leading-relaxed">
            You commit to respecting the rights of other users and the original artists, not using Dorémix for illicit purposes, and not interfering with the service's proper operation (e.g., through bots, DDoS, or scraping).
          </p>
        </section>

        <p class="text-sm text-neutral-500 mt-12 pt-6 border-t border-white/10">
          Last updated: April 2026
        </p>
      </div>
    </div>
  );

  container.innerHTML = content;
}
