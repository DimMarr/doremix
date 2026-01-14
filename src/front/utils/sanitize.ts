import DOMPurify from 'dompurify';

export class Sanitize {
  /**
   * Vérifie si un chemin est valide et sûr à utiliser
   * @param path - Le chemin à vérifier
   * @returns true si le chemin est valide, false sinon
   */
  isValidPath(path: string | null | undefined): boolean {
    if (!path || typeof path !== 'string') return false;

    // Vérifier les schémas interdits
    const lowerPath = path.toLowerCase().trim();
    const forbiddenSchemes = ['javascript:', 'data:', 'vbscript:', 'file:', 'about:'];

    if (forbiddenSchemes.some(scheme => lowerPath.startsWith(scheme))) {
      return false;
    }

    // Vérifier que le chemin commence par /
    if (!path.startsWith('/')) {
      return false;
    }

    // Empecher les chemins relatifs
    if (path.includes('..')) {
      return false;
    }

    return true;
  }

  /**
   * Nettoie un chemin pour s'assurer qu'il est sûr à utiliser
   * @param path - Le chemin à nettoyer
   * @returns Le chemin nettoyé
   */
  sanitizePath(path: string | null | undefined): string {
    if (!path) return '/';

    // Nettoyage avec DOMPurify
    let sanitized = DOMPurify.sanitize(path, {
      ALLOWED_TAGS: [],
      ALLOWED_ATTR: [],
      KEEP_CONTENT: true
    });

    // Supprimer les caractères nuls
    sanitized = sanitized.replace(/\0/g, '');

    // Supprimer les caractères potentiellement dangereux
    sanitized = sanitized.replace(/[<>'"]/g, '');

  // S'assurer que le chemin commence par /
    if (!sanitized.startsWith('/')) {
      sanitized = '/' + sanitized;
    }

    // Encodage du chemin
    return encodeURI(sanitized);
  }

  /**
   * Encodes un chemin avec des paramètres de manière sécurisée
   * @param basePath - Le chelin de base avec les place-holders (par exemple : "/user/:id")
   * @param params - Object qui contient les paramètres à insérer dans le chemin
   * @returns Le chemin encodé avec les paramètres insérés de manière sécurisée
   */
  encodePath(basePath: string, params: Record<string, string | number> = {}): string {
    let encoded = basePath;

    for (const [key, value] of Object.entries(params)) {
      // On nettoie et encode chaque valeur de paramètre
      const sanitizedValue = DOMPurify.sanitize(String(value), {
        ALLOWED_TAGS: [],
        ALLOWED_ATTR: [],
        KEEP_CONTENT: true
      });
      const encodedValue = encodeURIComponent(sanitizedValue);
      encoded = encoded.replace(`:${key}`, encodedValue);
    }

    return encoded;
  }

  /**
   * Nettoie les paramètres d'une route pour éviter les injections XSS
   * @param params - Objet qui contient les paramètres à nettoyer
   * @returns Objet contenant les paramètres nettoyés
   */
  sanitizeParams(params: Record<string, string>): Record<string, string> {
    const sanitized: Record<string, string> = {};

    for (const [key, value] of Object.entries(params)) {
      sanitized[key] = DOMPurify.sanitize(value, {
        ALLOWED_TAGS: [],
        ALLOWED_ATTR: [],
        KEEP_CONTENT: true
      });
    }

    return sanitized;
  }

}
