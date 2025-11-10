export default function PaperCard({ paper }) {
  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      {/* Title */}
      <h4 className="font-semibold text-gray-900 mb-2 leading-snug">
        {paper.title}
      </h4>

      {/* Authors and Year */}
      <div className="flex items-center text-sm text-gray-600 mb-2">
        <span className="font-medium">
          {paper.authors && paper.authors.length > 0
            ? paper.authors.slice(0, 3).join(', ') + (paper.authors.length > 3 ? ' et al.' : '')
            : 'Autor desconocido'}
        </span>
        {paper.year && (
          <>
            <span className="mx-2">•</span>
            <span>{paper.year}</span>
          </>
        )}
      </div>

      {/* Abstract Preview */}
      {paper.abstract && (
        <p className="text-sm text-gray-700 mb-3 line-clamp-3">
          {paper.abstract}
        </p>
      )}

      {/* Metadata */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-3">
          {paper.citations !== null && paper.citations !== undefined && (
            <span className="flex items-center">
              <span className="mr-1">📖</span>
              {paper.citations} citas
            </span>
          )}
          {paper.source && (
            <span className="px-2 py-1 bg-white rounded-full border border-gray-200">
              {paper.source}
            </span>
          )}
        </div>

        {/* Link to Paper */}
        {paper.url && (
          <a
            href={paper.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center text-blue-600 hover:text-blue-800 font-medium"
          >
            Ver paper
            <svg
              className="w-4 h-4 ml-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        )}
      </div>
    </div>
  );
}
