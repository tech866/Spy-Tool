/**
 * Tag component for displaying ad tags
 */

interface TagProps {
  name: string;
  onRemove?: () => void;
  clickable?: boolean;
  onClick?: () => void;
}

export default function Tag({ name, onRemove, clickable, onClick }: TagProps) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-primary/20 text-primary text-xs font-medium ${
        clickable ? 'cursor-pointer hover:bg-primary/30' : ''
      }`}
      onClick={onClick}
    >
      {name}
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="hover:text-red-400"
        >
          ×
        </button>
      )}
    </span>
  );
}
