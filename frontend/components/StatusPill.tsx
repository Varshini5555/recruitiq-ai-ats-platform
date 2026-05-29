interface Props {
  text: string;
  type: "green" | "yellow" | "red" | "blue";
}

export default function StatusPill({
  text,
  type,
}: Props) {

  const styles = {
    green: "bg-green-100 text-green-700",
    yellow: "bg-yellow-100 text-yellow-700",
    red: "bg-red-100 text-red-700",
    blue: "bg-blue-100 text-blue-700",
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-medium ${styles[type]}`}
    >
      {text}
    </span>
  );
}